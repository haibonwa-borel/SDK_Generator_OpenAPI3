using System;
using System.IO;
using SDKGenerator.Generators;

class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("Testing SdkGeneratorEngine...");

        var baseDir = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "../../../../"));
        
        string[] samples = { "petstore.yaml", "users_api.json" };

        foreach (var sample in samples)
        {
            Console.WriteLine($"\n--- Generating SDK for {sample} ---");
            string inputPath = Path.Combine(baseDir, "samples", sample);
            string outputDir = Path.Combine(baseDir, "sdk_output", Path.GetFileNameWithoutExtension(sample));
            
            var generator = new SdkGeneratorEngine(inputPath, outputDir, "TestSDK", msg => Console.WriteLine(msg));
            try
            {
                generator.Generate();
                Console.WriteLine("SUCCESS!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"FAILED: {ex.Message}");
            }
        }
    }
}
