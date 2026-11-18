using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using Microsoft.Win32;

namespace Liga1Orange.Launcher
{
    /// <summary>Paths next to the launcher and the small settings file.</summary>
    public static class AppPaths
    {
        public static readonly string BaseDir = AppDomain.CurrentDomain.BaseDirectory;
        public static string ToolsDir => Path.Combine(BaseDir, "tools");
        public static string FrostyExe => Path.Combine(ToolsDir, "FrostyCmd.exe");
        public static string ModsDir => Path.Combine(BaseDir, "mods");
        public static string VersionFile => Path.Combine(ModsDir, "version.txt");
        public static string DataDir => Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "Liga1OrangeLauncher");
        public static string LogDir => Path.Combine(DataDir, "logs");
        public static string SettingsFile => Path.Combine(DataDir, "settings.txt");
    }

    public static class Settings
    {
        public static string Get(string key)
        {
            try
            {
                if (!File.Exists(AppPaths.SettingsFile)) return null;
                foreach (string line in File.ReadAllLines(AppPaths.SettingsFile))
                {
                    int i = line.IndexOf('=');
                    if (i > 0 && line.Substring(0, i) == key) return line.Substring(i + 1);
                }
            }
            catch { }
            return null;
        }

        public static void Set(string key, string value)
        {
            try
            {
                Directory.CreateDirectory(AppPaths.DataDir);
                var lines = File.Exists(AppPaths.SettingsFile)
                    ? File.ReadAllLines(AppPaths.SettingsFile).Where(l => !l.StartsWith(key + "=")).ToList()
                    : new List<string>();
                lines.Add(key + "=" + value);
                File.WriteAllLines(AppPaths.SettingsFile, lines);
            }
            catch { }
        }
    }

    /// <summary>
    /// A zip downloaded in a browser marks every extracted file with a Zone.Identifier stream (Mark of the Web) and .NET Framework
    /// then refuses to load such assemblies with Assembly.LoadFile ("an attempt was made to load an assembly from a network
    /// location"). Removing the stream unblocks them (same as "Unblock" in the file properties).
    /// </summary>
    public static class Unblocker
    {
        [System.Runtime.InteropServices.DllImport("kernel32.dll", CharSet = System.Runtime.InteropServices.CharSet.Unicode, SetLastError = true)]
        static extern bool DeleteFile(string path);

        public static int UnblockTree(string dir)
        {
            int n = 0;
            try
            {
                if (!Directory.Exists(dir)) return 0;
                foreach (string f in Directory.EnumerateFiles(dir, "*", SearchOption.AllDirectories))
                    if (DeleteFile(f + ":Zone.Identifier")) n++;
            }
            catch { }
            return n;
        }
    }

    public static class GameLocator
    {
        public static bool IsGameDir(string dir)
        {
            return !string.IsNullOrEmpty(dir) && File.Exists(Path.Combine(dir, "FIFA17.exe"));
        }

        /// <summary>Saved folder, the installer registry keys, then the usual places.</summary>
        public static string Find()
        {
            var candidates = new List<string> { Settings.Get("gamepath") };
            foreach (string key in new[]
            {
                @"SOFTWARE\WOW6432Node\EA Games\FIFA 17", @"SOFTWARE\EA Games\FIFA 17",
                @"SOFTWARE\WOW6432Node\Origin Games\FIFA 17", @"SOFTWARE\Origin Games\FIFA 17"
            })
            {
                try
                {
                    using (RegistryKey k = Registry.LocalMachine.OpenSubKey(key))
                    {
                        string v = k?.GetValue("Install Dir") as string ?? k?.GetValue("InstallDir") as string;
                        if (!string.IsNullOrEmpty(v)) candidates.Add(v.TrimEnd('\\'));
                    }
                }
                catch { }
            }
            foreach (DriveInfo d in DriveInfo.GetDrives().Where(x => x.DriveType == DriveType.Fixed))
            {
                string r = d.RootDirectory.FullName;
                candidates.Add(Path.Combine(r, "Games", "FIFA 17"));
                candidates.Add(Path.Combine(r, "FIFA 17"));
                candidates.Add(Path.Combine(r, "Program Files (x86)", "Origin Games", "FIFA 17"));
                candidates.Add(Path.Combine(r, "Program Files", "EA Games", "FIFA 17"));
                candidates.Add(Path.Combine(r, "Program Files (x86)", "EA Games", "FIFA 17"));
            }
            return candidates.FirstOrDefault(IsGameDir);
        }

        /// <summary>The patched CryptBase.dll is about 95 KB; the Windows one is about 70 KB.</summary>
        public static bool HasPatchedCryptBase(string dir)
        {
            try
            {
                var fi = new FileInfo(Path.Combine(dir, "CryptBase.dll"));
                return fi.Exists && fi.Length > 90000;
            }
            catch { return false; }
        }
    }

    public class ReleaseInfo
    {
        public string Tag;
        public string Name;
        public string AssetName;
        public string AssetUrl;
        public bool Prerelease;
    }

    /// <summary>Looks for the newest .fbmod on the project's GitHub Releases and downloads it. Sends no personal data.</summary>
    public static class Updater
    {
        const string Api = "https://api.github.com/repos/Gabarsolon/fifa-17-liga-1-orange/releases?per_page=10";

        static WebClient Client()
        {
            ServicePointManager.SecurityProtocol |= (SecurityProtocolType)3072; // TLS 1.2
            var c = new WebClient { Encoding = Encoding.UTF8 };
            c.Headers[HttpRequestHeader.UserAgent] = "Liga1OrangeLauncher";
            return c;
        }

        public static string InstalledTag()
        {
            try { return File.Exists(AppPaths.VersionFile) ? File.ReadAllText(AppPaths.VersionFile).Trim() : null; }
            catch { return null; }
        }

        public static string InstalledModPath()
        {
            string tag = InstalledTag();
            if (!string.IsNullOrEmpty(tag))
            {
                string p = Path.Combine(AppPaths.ModsDir, "Liga1Orange-" + tag + ".fbmod");
                if (File.Exists(p)) return p;
            }
            if (!Directory.Exists(AppPaths.ModsDir)) return null;
            return Directory.GetFiles(AppPaths.ModsDir, "*.fbmod").OrderByDescending(f => new FileInfo(f).LastWriteTimeUtc).FirstOrDefault();
        }

        [DataContract]
        class AssetDto
        {
            [DataMember(Name = "name")] public string Name;
            [DataMember(Name = "browser_download_url")] public string Url;
        }

        [DataContract]
        class ReleaseDto
        {
            [DataMember(Name = "tag_name")] public string Tag;
            [DataMember(Name = "name")] public string Name;
            [DataMember(Name = "draft")] public bool Draft;
            [DataMember(Name = "prerelease")] public bool Prerelease;
            [DataMember(Name = "assets")] public AssetDto[] Assets;
        }

        public static ReleaseInfo Latest()
        {
            byte[] json;
            using (WebClient c = Client()) json = c.DownloadData(Api);
            ReleaseDto[] list;
            using (var ms = new MemoryStream(json))
                list = (ReleaseDto[])new DataContractJsonSerializer(typeof(ReleaseDto[])).ReadObject(ms);
            foreach (ReleaseDto item in list ?? new ReleaseDto[0])
            {
                if (item.Draft) continue;
                AssetDto fbmod = item.Assets?.FirstOrDefault(a => a.Name != null && a.Name.EndsWith(".fbmod", StringComparison.OrdinalIgnoreCase));
                if (fbmod == null) continue;
                return new ReleaseInfo { Tag = item.Tag, Name = item.Name, Prerelease = item.Prerelease, AssetName = fbmod.Name, AssetUrl = fbmod.Url };
            }
            return null;
        }

        public static string Download(ReleaseInfo r)
        {
            Directory.CreateDirectory(AppPaths.ModsDir);
            string target = Path.Combine(AppPaths.ModsDir, "Liga1Orange-" + r.Tag + ".fbmod");
            string tmp = target + ".part";
            using (WebClient c = Client()) c.DownloadFile(r.AssetUrl, tmp);
            if (File.Exists(target)) File.Delete(target);
            File.Move(tmp, target);
            File.WriteAllText(AppPaths.VersionFile, r.Tag);
            return target;
        }
    }

    /// <summary>Runs FrostyCmd apply-mods (it builds the mod pack and starts the game) and reports its output.</summary>
    public class FrostyRunner
    {
        public event Action<string> Line;
        Process _process;

        public bool IsRunning => _process != null && !_process.HasExited;

        public Task<int> ApplyAndLaunch(string gameDir, string modPath)
        {
            return Task.Run(() =>
            {
                var psi = new ProcessStartInfo(AppPaths.FrostyExe, "FIFA17 apply-mods Liga1Orange \"" + modPath + "\"")
                {
                    WorkingDirectory = AppPaths.ToolsDir,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    StandardOutputEncoding = Encoding.UTF8
                };
                psi.EnvironmentVariables["FIFA17_DIR"] = gameDir;
                _process = Process.Start(psi);
                DataReceivedEventHandler handler = (s, e) => { if (e.Data != null) Line?.Invoke(e.Data); };
                _process.OutputDataReceived += handler;
                _process.ErrorDataReceived += handler;
                _process.BeginOutputReadLine();
                _process.BeginErrorReadLine();
                _process.WaitForExit();
                return _process.ExitCode;
            });
        }

        public void Stop()
        {
            try { if (IsRunning) _process.Kill(); } catch { }
        }
    }
}
