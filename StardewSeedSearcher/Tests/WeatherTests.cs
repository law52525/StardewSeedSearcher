using System;
using System.Linq;
using StardewSeedSearcher.Features;
using System.Collections.Generic;

namespace StardewSeedSearcher.Tests
{
    /// <summary>
    /// 天气预测功能测试
    /// </summary>
    public static class WeatherTests
    {
        public static void Run()
        {
            Console.WriteLine("=== 天气预测测试 ===\n");

            // 输入种子
            Console.Write("请输入游戏种子：");
            string input = Console.ReadLine();
            
            if (!int.TryParse(input, out int gameID))
            {
                Console.WriteLine("无效的种子，请输入整数");
                return;
            }

            // 选择随机模式
            Console.Write("使用旧随机模式？(y/n，默认 n)：");
            string modeInput = Console.ReadLine()?.Trim().ToLower();
            bool useLegacyRandom = modeInput == "y" || modeInput == "yes";

            // 预测天气
            var predictor = new WeatherPredictor();
            var rainyDays = predictor.PredictSpringRain(gameID, useLegacyRandom);

            // 输出结果
            Console.WriteLine($"\n种子：{gameID}");
            
            if (rainyDays.Count > 0)
            {
                string rainyDaysStr = string.Join("，", rainyDays.Select(d => $"春{d}"));
                Console.WriteLine($"春季雨天：{rainyDaysStr}");
            }
            else
            {
                Console.WriteLine("春季雨天：无");
            }
            
            Console.WriteLine($"雨天总数：{rainyDays.Count}");

            // 显示所有天气详情（可选）
            Console.Write("\n是否显示全部28天的天气详情？(y/n)：");
            string detailInput = Console.ReadLine()?.Trim().ToLower();
            
            if (detailInput == "y" || detailInput == "yes")
            {
                ShowDetailedWeather(gameID, useLegacyRandom, rainyDays);
            }
        }

        /// <summary>
        /// 显示春季所有天气详情
        /// </summary>
        private static void ShowDetailedWeather(int gameID, bool useLegacy, List<int> rainyDays)
        {
            Console.WriteLine("\n春季天气详情：");
            Console.WriteLine("日期\t天气");
            Console.WriteLine("-------------------");
            
            for (int day = 1; day <= 28; day++)
            {
                string weather = rainyDays.Contains(day) ? "雨天" : "晴天";
                Console.WriteLine($"春{day}\t{weather}");
            }
        }
    }
}