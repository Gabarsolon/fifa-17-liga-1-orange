using System.Threading;
using System.Windows;

namespace Liga1Orange.Launcher
{
    public partial class App : Application
    {
        static Mutex _single;

        protected override void OnStartup(StartupEventArgs e)
        {
            bool created;
            _single = new Mutex(true, "Liga1OrangeLauncher-single-instance", out created);
            if (!created)
            {
                MessageBox.Show("Launcherul rulează deja.", "Liga 1 Orange", MessageBoxButton.OK, MessageBoxImage.Information);
                Shutdown();
                return;
            }
            base.OnStartup(e);
        }
    }
}
