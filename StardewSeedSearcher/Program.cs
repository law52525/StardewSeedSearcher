using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using StardewSeedSearcher.Features;

namespace StardewSeedSearcher
{
    /// <summary>
    /// 主程序：批量搜索符合条件的种子
    /// </summary>
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=================================");
            Console.WriteLine("  星露谷物语 - 种子搜索器");
            Console.WriteLine("=================================\n");

            // 配置搜索范围
            Console.Write("起始种子（默认 0）：");
            string startInput = Console.ReadLine();
            int startSeed = string.IsNullOrWhiteSpace(startInput) ? 0 : int.Parse(startInput);

            Console.Write("结束种子（默认 100000）：");
            string endInput = Console.ReadLine();
            int endSeed = string.IsNullOrWhiteSpace(endInput) ? 100000 : int.Parse(endInput);

            // 选择随机模式
            Console.Write("使用旧随机模式？(y/n，默认 n)：");
            string modeInput = Console.ReadLine()?.Trim().ToLower();
            bool useLegacyRandom = modeInput == "y" || modeInput == "yes";

            // 配置功能
            var features = ConfigureFeatures();

            // 显示配置摘要
            Console.WriteLine("\n=== 搜索配置 ===");
            Console.WriteLine($"种子范围：{startSeed} - {endSeed}");
            Console.WriteLine($"随机模式：{(useLegacyRandom ? "旧随机" : "新随机")}");
            Console.WriteLine($"启用功能：");
            foreach (var feature in features.Where(f => f.IsEnabled))
            {
                Console.WriteLine($"  - {feature.Name}: {feature.GetConfigDescription()}");
            }

            Console.Write("\n按任意键开始搜索...");
            Console.ReadKey();
            Console.WriteLine("\n");

            // 开始搜索
            SearchSeeds(startSeed, endSeed, useLegacyRandom, features);

            Console.WriteLine("\n搜索完成！按任意键退出...");
            Console.ReadKey();
        }

        /// <summary>
        /// 配置搜索功能
        /// </summary>
        static List<ISearchFeature> ConfigureFeatures()
        {
            var features = new List<ISearchFeature>();

            // 天气预测功能
            Console.WriteLine("\n=== 功能 1: 天气预测 ===");
            Console.Write("是否启用？(y/n，默认 y)：");
            string enableWeather = Console.ReadLine()?.Trim().ToLower();
            bool weatherEnabled = enableWeather != "n" && enableWeather != "no";

            if (weatherEnabled)
            {
                Console.Write("春季最少雨天数（默认 10）：");
                string minRainInput = Console.ReadLine();
                int minRain = string.IsNullOrWhiteSpace(minRainInput) ? 10 : int.Parse(minRainInput);

                features.Add(new WeatherPredictor
                {
                    IsEnabled = true,
                    MinRainyDays = minRain
                });
            }
            else
            {
                features.Add(new WeatherPredictor { IsEnabled = false });
            }

            // 未来添加更多功能...

            return features;
        }

        /// <summary>
        /// 批量搜索种子
        /// </summary>
        static void SearchSeeds(int start, int end, bool useLegacy, List<ISearchFeature> features)
        {
            var matchedSeeds = new List<int>();
            var stopwatch = Stopwatch.StartNew();
            int totalSeeds = end - start + 1;
            int checkedCount = 0;

            Console.WriteLine("正在搜索种子...\n");

            for (int seed = start; seed <= end; seed++)
            {
                checkedCount++;

                // 检查是否符合所有启用的功能条件
                bool allMatch = true;
                foreach (var feature in features.Where(f => f.IsEnabled))
                {
                    if (!feature.Check(seed, useLegacy))
                    {
                        allMatch = false;
                        break;
                    }
                }

                if (allMatch)
                {
                    matchedSeeds.Add(seed);
                    Console.WriteLine($"找到符合条件的种子: {seed}");
                }

                // 显示进度（每1000个种子）
                if (checkedCount % 1000 == 0)
                {
                    double progress = (double)checkedCount / totalSeeds * 100;
                    Console.Write($"\r进度: {progress:F1}% ({checkedCount}/{totalSeeds})");
                }
            }

            stopwatch.Stop();

            // 输出结果
            Console.WriteLine($"\n\n=== 搜索结果 ===");
            Console.WriteLine($"检查种子数: {totalSeeds}");
            Console.WriteLine($"符合条件: {matchedSeeds.Count}");
            Console.WriteLine($"用时: {stopwatch.Elapsed.TotalSeconds:F2} 秒");
            Console.WriteLine($"速度: {totalSeeds / stopwatch.Elapsed.TotalSeconds:F0} 种子/秒");

            if (matchedSeeds.Count > 0)
            {
                Console.WriteLine($"\n符合条件的种子列表:");
                foreach (int seed in matchedSeeds)
                {
                    Console.WriteLine($"  {seed}");
                }
            }
        }
    }
}