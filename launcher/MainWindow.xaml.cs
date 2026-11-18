using System;
using System.Collections.Concurrent;
using System.Text.RegularExpressions;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Principal;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Documents;
using System.Windows.Media;
using System.Windows.Navigation;
using System.Windows.Threading;
using Forms = System.Windows.Forms;

namespace Liga1Orange.Launcher
{
    public partial class MainWindow : Window
    {
        readonly FrostyRunner _runner = new FrostyRunner();
        readonly StringBuilder _log = new StringBuilder();
        readonly DispatcherTimer _timer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(2) };
        readonly DispatcherTimer _flush = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(150) };
        readonly ConcurrentQueue<string> _queue = new ConcurrentQueue<string>();
        string _lastRaw;
        volatile string _percent;
        string _shownPercent;
        string _gameDir;
        bool _modRunning;
        string _logFile;

        public MainWindow()
        {
            InitializeComponent();
            // tall enough to show the whole log, but never taller than the screen
            Height = Math.Min(940, SystemParameters.WorkArea.Height - 30);
            Top = Math.Max(0, (SystemParameters.WorkArea.Height - Height) / 2);
            LauncherVersionText.Text = "Launcher " + typeof(MainWindow).Assembly.GetName().Version.ToString(2);
            _runner.Line += OnFrostyOutput; // runs on a worker thread: filter here, never flood the UI thread
            _flush.Tick += (s, e) => FlushLog();
            _flush.Start();
            _timer.Tick += (s, e) => RefreshGameRunning();
            _timer.Start();
            Loaded += async (s, e) => await Startup();
        }

        // ---------- startup ----------

        async Task Startup()
        {
            Directory.CreateDirectory(AppPaths.LogDir);
            _logFile = Path.Combine(AppPaths.LogDir, "launcher-" + DateTime.Now.ToString("yyyyMMdd-HHmmss") + ".log");
            int unblocked = await Task.Run(() => Unblocker.UnblockTree(AppPaths.ToolsDir) + Unblocker.UnblockTree(AppPaths.ModsDir));
            if (unblocked > 0) Log("Am deblocat " + unblocked + " fișiere descărcate din internet.");
            _gameDir = GameLocator.Find();
            if (_gameDir != null) Settings.Set("gamepath", _gameDir);
            RefreshChecks();
            RefreshModText();
            SetStatus("Pregătit", "ok");
            if (_gameDir == null)
                Log("Nu am găsit FIFA 17. Apasă „Alege folderul…” și selectează folderul care conține FIFA17.exe.");
            if (Updater.InstalledModPath() == null || Settings.Get("autoupdate") != "off")
                await CheckUpdates(silent: true);
            // "Liga1OrangeLauncher.exe --play" starts the game right away (for a desktop shortcut)
            if (Environment.GetCommandLineArgs().Contains("--play") && PlayButton.IsEnabled)
                PlayButton_Click(this, new RoutedEventArgs());
        }

        static bool IsAdmin()
        {
            using (WindowsIdentity id = WindowsIdentity.GetCurrent())
                return new WindowsPrincipal(id).IsInRole(WindowsBuiltInRole.Administrator);
        }

        void SetChip(System.Windows.Controls.TextBlock chip, string text, string state)
        {
            chip.Text = "● " + text;
            chip.Foreground = (Brush)FindResource(state == "ok" ? "OkBrush" : state == "warn" ? "WarnBrush" : "BadBrush");
        }

        void RefreshChecks()
        {
            bool game = GameLocator.IsGameDir(_gameDir);
            GamePathText.Text = game ? _gameDir : "Folderul FIFA 17 nu a fost găsit";
            SetChip(ChipExe, "FIFA17.exe", game ? "ok" : "bad");
            // Frosty's executor copies its own ThirdParty\CryptBase.dll into the game folder on the first apply, so a missing file is normal.
            bool crypt = game && GameLocator.HasPatchedCryptBase(_gameDir);
            SetChip(ChipCrypt, crypt ? "CryptBase.dll" : "CryptBase.dll (o instalează Frosty la prima pornire)", !game ? "bad" : "ok");
            bool admin = IsAdmin();
            SetChip(ChipAdmin, admin ? "Drepturi de administrator" : "Fără drepturi de administrator", admin ? "ok" : "warn");
            bool tools = File.Exists(AppPaths.FrostyExe);
            SetChip(ChipTools, tools ? "Frosty" : "Frosty lipsește (folderul tools)", tools ? "ok" : "bad");
            UpdatePlayEnabled();
        }

        void RefreshModText()
        {
            string tag = Updater.InstalledTag();
            string mod = Updater.InstalledModPath();
            ModVersionText.Text = "Mod: " + (tag ?? (mod != null ? Path.GetFileNameWithoutExtension(mod) : "—"));
            ModText.Text = mod != null ? "Liga 1 Orange " + (tag ?? "") : "Modul nu este descărcat încă";
            UpdatePlayEnabled();
        }

        void UpdatePlayEnabled()
        {
            bool ready = GameLocator.IsGameDir(_gameDir) && File.Exists(AppPaths.FrostyExe) && Updater.InstalledModPath() != null;
            PlayButton.IsEnabled = ready && !_modRunning;
            VanillaButton.IsEnabled = GameLocator.IsGameDir(_gameDir) && !_modRunning;
        }

        // ---------- status and log ----------

        void SetStatus(string text, string state, bool busy = false)
        {
            StatusText.Text = text;
            StatusDot.Fill = (Brush)FindResource(state == "ok" ? "OkBrush" : state == "warn" ? "WarnBrush" : "BadBrush");
            Busy.Visibility = busy ? Visibility.Visible : Visibility.Collapsed;
        }

        void Log(string line)
        {
            string stamped = DateTime.Now.ToString("HH:mm:ss") + "  " + line;
            _log.AppendLine(stamped);
            LogBox.AppendText(stamped + Environment.NewLine);
            TrimLogBox();
            LogBox.ScrollToEnd();
            try { if (_logFile != null) File.AppendAllText(_logFile, stamped + Environment.NewLine); } catch { }
        }

        void TrimLogBox()
        {
            if (LogBox.LineCount > 500)
            {
                string[] lines = LogBox.Text.Split('\n');
                LogBox.Text = string.Join("\n", lines.Skip(lines.Length - 300));
            }
        }

        // Frosty prints thousands of lines (progress:, "Loading Data (...)", "Initial load - Indexing data (2%)" repeated):
        // they are dropped or reduced to a percentage here, on the worker thread.
        void OnFrostyOutput(string raw)
        {
            if (raw.Contains("progress:")) return;
            string line = Regex.Replace(raw, @"^\[[^\]]*\]:\s*", "").Trim();
            if (line.Length == 0 || line == _lastRaw) return;
            _lastRaw = line;
            if (line.StartsWith("Loading Data (")) return;
            Match m = Regex.Match(line, @"\((\d+)%\)");
            if (m.Success) { _percent = m.Groups[1].Value; return; }
            _queue.Enqueue(line);
        }

        void FlushLog()
        {
            string pct = _percent;
            if (pct != null && pct != _shownPercent && _modRunning)
            {
                _shownPercent = pct;
                SetStatus("Se pregătește cache-ul jocului (doar la prima pornire, ~4 minute): " + pct + "%", "warn", true);
            }
            var batch = new StringBuilder();
            string line;
            int n = 0;
            while (n < 80 && _queue.TryDequeue(out line))
            {
                n++;
                string stamped = DateTime.Now.ToString("HH:mm:ss") + "  " + line;
                _log.AppendLine(stamped);
                batch.AppendLine(stamped);
                if (line.StartsWith("Applying")) SetStatus("Se aplică modul…", "warn", true);
                else if (line.StartsWith("Launching Game")) SetStatus("Se pornește jocul…", "warn", true);
                else if (line.Contains("Game launched successfully")) SetStatus("Jocul rulează", "ok");
                else if (line.StartsWith("Loading Complete")) SetStatus("Cache gata, se aplică modul…", "warn", true);
            }
            if (n == 0) return;
            LogBox.AppendText(batch.ToString());
            TrimLogBox();
            LogBox.ScrollToEnd();
            try { if (_logFile != null) File.AppendAllText(_logFile, batch.ToString()); } catch { }
        }

        void RefreshGameRunning()
        {
            bool running = Process.GetProcessesByName("FIFA17").Length > 0;
            if (running && _modRunning && StatusText.Text.StartsWith("Se pornește"))
                SetStatus("Jocul rulează", "ok");
        }

        // ---------- actions ----------

        void BrowseButton_Click(object sender, RoutedEventArgs e)
        {
            using (var dlg = new Forms.FolderBrowserDialog { Description = "Alege folderul FIFA 17 (cel cu FIFA17.exe)", ShowNewFolderButton = false })
            {
                if (_gameDir != null && Directory.Exists(_gameDir)) dlg.SelectedPath = _gameDir;
                if (dlg.ShowDialog() != Forms.DialogResult.OK) return;
                if (!GameLocator.IsGameDir(dlg.SelectedPath))
                {
                    MessageBox.Show(this, "În folderul ales nu există FIFA17.exe.", "Folder greșit", MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }
                _gameDir = dlg.SelectedPath;
                Settings.Set("gamepath", _gameDir);
                Log("Folder FIFA 17: " + _gameDir);
                RefreshChecks();
            }
        }

        async void UpdateButton_Click(object sender, RoutedEventArgs e)
        {
            await CheckUpdates(silent: false);
        }

        async Task CheckUpdates(bool silent)
        {
            UpdateButton.IsEnabled = false;
            UpdateText.Text = "Se verifică GitHub…";
            try
            {
                ReleaseInfo latest = await Task.Run(() => Updater.Latest());
                string installed = Updater.InstalledTag();
                if (latest == null)
                {
                    UpdateText.Text = "Nu am găsit nicio versiune publicată.";
                }
                else if (installed == latest.Tag && Updater.InstalledModPath() != null)
                {
                    UpdateText.Text = "Ai cea mai nouă versiune (" + latest.Tag + ")" + (latest.Prerelease ? ", pre-release." : ".");
                }
                else
                {
                    UpdateText.Text = "Se descarcă " + latest.Tag + "…";
                    SetStatus("Se descarcă modul " + latest.Tag + "…", "warn", true);
                    string path = await Task.Run(() => Updater.Download(latest));
                    Log("Descărcat " + Path.GetFileName(path));
                    UpdateText.Text = "Actualizat la " + latest.Tag + (latest.Prerelease ? " (pre-release)." : ".");
                    SetStatus("Pregătit", "ok");
                }
            }
            catch (Exception ex)
            {
                bool notPublic = ex.Message.Contains("404");
                UpdateText.Text = notPublic
                    ? "Actualizările automate vor funcționa când versiunile sunt publice. Poți juca cu versiunea inclusă."
                    : silent ? "Nu m-am putut conecta la GitHub (poți juca cu versiunea instalată)." : "Eroare la verificare: " + ex.Message;
                Log("Actualizare: " + ex.Message);
                SetStatus("Pregătit", "ok");
            }
            finally
            {
                UpdateButton.IsEnabled = true;
                RefreshModText();
            }
        }

        async void PlayButton_Click(object sender, RoutedEventArgs e)
        {
            string mod = Updater.InstalledModPath();
            if (!GameLocator.IsGameDir(_gameDir) || mod == null) return;
            if (!IsAdmin())
                Log("Atenție: launcherul nu rulează ca administrator, aplicarea modului poate eșua. Pornește-l cu clic dreapta → Run as administrator.");
            if (FrostyRunningFromThisFolder())
            {
                MessageBox.Show(this, "Frosty rulează deja (poate dintr-o altă fereastră a launcherului). Așteaptă să termine sau închide-l din Task Manager (FrostyCmd.exe), apoi încearcă din nou.",
                    "Frosty rulează", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }
            if (Process.GetProcessesByName("FIFA17").Length > 0)
            {
                MessageBox.Show(this, "FIFA 17 rulează deja. Închide jocul și încearcă din nou.", "Joc pornit", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }
            _modRunning = true;
            UpdatePlayEnabled();
            SetStatus("Se pregătește modul…", "warn", true);
            await Task.Run(() => Unblocker.UnblockTree(AppPaths.ToolsDir));
            Log("Aplic " + Path.GetFileName(mod) + " și pornesc jocul…");
            try
            {
                int code = await _runner.ApplyAndLaunch(_gameDir, mod);
                Log("Frosty s-a încheiat (cod " + code + ").");
                SetStatus(code == 0 ? "Pregătit" : "Ceva nu a mers (vezi jurnalul)", code == 0 ? "ok" : "bad");
            }
            catch (Exception ex)
            {
                Log("Eroare: " + ex.Message);
                SetStatus("Eroare la pornire (vezi jurnalul)", "bad");
            }
            finally
            {
                _modRunning = false;
                UpdatePlayEnabled();
            }
        }

        /// <summary>A second Frosty on the same tools folder would write the same cache file at the same time.</summary>
        static bool FrostyRunningFromThisFolder()
        {
            foreach (Process p in Process.GetProcessesByName("FrostyCmd"))
            {
                try
                {
                    if (string.Equals(p.MainModule.FileName, Path.GetFullPath(AppPaths.FrostyExe), StringComparison.OrdinalIgnoreCase))
                        return true;
                }
                catch { }
            }
            return false;
        }

        void VanillaButton_Click(object sender, RoutedEventArgs e)
        {
            if (!GameLocator.IsGameDir(_gameDir)) return;
            try
            {
                Process.Start(new ProcessStartInfo(Path.Combine(_gameDir, "FIFA17.exe")) { WorkingDirectory = _gameDir, UseShellExecute = true });
                Log("Am pornit jocul original.");
            }
            catch (Exception ex)
            {
                Log("Eroare: " + ex.Message);
            }
        }

        void LogFolderButton_Click(object sender, RoutedEventArgs e)
        {
            Directory.CreateDirectory(AppPaths.LogDir);
            Process.Start("explorer.exe", AppPaths.LogDir);
        }

        void Link_Navigate(object sender, RequestNavigateEventArgs e)
        {
            Process.Start(new ProcessStartInfo(e.Uri.AbsoluteUri) { UseShellExecute = true });
            e.Handled = true;
        }

        protected override void OnClosing(System.ComponentModel.CancelEventArgs e)
        {
            if (_runner.IsRunning &&
                MessageBox.Show(this, "Modul încă se aplică. Sigur închizi launcherul?", "Launcher", MessageBoxButton.YesNo, MessageBoxImage.Question) != MessageBoxResult.Yes)
            {
                e.Cancel = true;
                return;
            }
            base.OnClosing(e);
        }
    }
}
