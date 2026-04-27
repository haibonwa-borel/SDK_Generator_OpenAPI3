using Microsoft.Win32;
using System;
using System.IO;
using System.Threading.Tasks;
using System.Windows;

namespace SDKGenerator
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        private void BtnBrowseInput_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog
            {
                Filter = "OpenAPI files (*.json;*.yaml;*.yml)|*.json;*.yaml;*.yml|All files (*.*)|*.*",
                Title = "Sélectionner un fichier OpenAPI"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                TxtInputFile.Text = openFileDialog.FileName;
            }
        }

        private void BtnBrowseOutput_Click(object sender, RoutedEventArgs e)
        {
            OpenFolderDialog openFolderDialog = new OpenFolderDialog
            {
                Title = "Sélectionner le dossier de sortie"
            };

            if (openFolderDialog.ShowDialog() == true)
            {
                TxtOutputFolder.Text = openFolderDialog.FolderName;
            }
        }

        private async void BtnGenerate_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(TxtInputFile.Text) || !File.Exists(TxtInputFile.Text))
            {
                MessageBox.Show("Veuillez sélectionner un fichier OpenAPI valide.", "Erreur", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            if (string.IsNullOrWhiteSpace(TxtOutputFolder.Text) || !Directory.Exists(TxtOutputFolder.Text))
            {
                MessageBox.Show("Veuillez sélectionner un dossier de sortie valide.", "Erreur", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            if (string.IsNullOrWhiteSpace(TxtSdkName.Text))
            {
                MessageBox.Show("Veuillez entrer un nom pour le SDK.", "Erreur", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            BtnGenerate.IsEnabled = false;
            TxtLogs.Text = "Démarrage de la génération...\n";

            try
            {
                string inputFilePath = TxtInputFile.Text;
                string outputDir = Path.Combine(TxtOutputFolder.Text, TxtSdkName.Text);
                string sdkName = TxtSdkName.Text;

                await Task.Run(() =>
                {
                    // Lancer le générateur
                    var generator = new Generators.SdkGeneratorEngine(
                        inputFilePath, 
                        outputDir, 
                        sdkName,
                        LogMessage);
                        
                    generator.Generate();
                });

                MessageBox.Show($"Génération terminée avec succès dans :\n{outputDir}", "Succès", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                LogMessage($"ERREUR : {ex.Message}");
                MessageBox.Show($"Une erreur est survenue :\n{ex.Message}", "Erreur de génération", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                BtnGenerate.IsEnabled = true;
            }
        }

        private void LogMessage(string message)
        {
            Dispatcher.Invoke(() =>
            {
                TxtLogs.AppendText(message + "\n");
                TxtLogs.ScrollToEnd();
            });
        }
    }
}