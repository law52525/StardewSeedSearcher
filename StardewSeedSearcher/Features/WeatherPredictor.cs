using System;
using System.Collections.Generic;
using StardewSeedSearcher.Core;

namespace StardewSeedSearcher.Features
{
    /// <summary>
    /// 天气预测功能
    /// 预测第一年春季的天气情况
    /// </summary>
    public class WeatherPredictor : ISearchFeature
    {
        /// <summary>筛选条件：春季最少雨天数</summary>
        public int MinRainyDays { get; set; } = 10;

        public string Name => "天气预测";
        public bool IsEnabled { get; set; } = true;

        /// <summary>
        /// 检查种子是否符合筛选条件
        /// </summary>
        public bool Check(int gameID, bool useLegacyRandom)
        {
            var rainyDays = PredictSpringRain(gameID, useLegacyRandom);
            return rainyDays.Count >= MinRainyDays;
        }

        /// <summary>
        /// 获取配置说明
        /// </summary>
        public string GetConfigDescription()
        {
            return $"春季雨天数 >= {MinRainyDays}";
        }
        /// <summary>
        /// 预测第一年春季的雨天日期
        /// </summary>
        /// <param name="gameID">游戏种子</param>
        /// <param name="useLegacyRandom">是否使用旧随机模式</param>
        /// <returns>雨天日期列表（1-28）</returns>
        public List<int> PredictSpringRain(int gameID, bool useLegacyRandom = false)
        {
            List<int> rainyDays = new List<int>();

            for (int day = 1; day <= 28; day++)
            {
                bool isRain = IsRainyDay(day, gameID, useLegacyRandom);
                
                if (isRain)
                {
                    rainyDays.Add(day);
                }
            }

            return rainyDays;
        }

        /// <summary>
        /// 判断春季某一天是否下雨
        /// </summary>
        private bool IsRainyDay(int day, int gameID, bool useLegacyRandom)
        {
            // 固定天气
            if (day == 1 || day == 2 || day == 4)
            {
                return false; // 晴天
            }
            else if (day == 3)
            {
                return true; // 雨天
            }
            else if (day == 13 || day == 24)
            {
                return false; // 节日（彩蛋节 13、花舞节 24）
            }
            else
            {
                // 计算随机天气
                // 对应 JS: getRandomSeed(getHashFromString("location_weather"), save.gameID, day-1)
                int locationWeatherHash = HashHelper.GetHashFromString("location_weather");
                int seed = HashHelper.GetRandomSeed(locationWeatherHash, gameID, day - 1, 0, 0, useLegacyRandom);
                
                Random rng = new Random(seed);
                double chance = rng.NextDouble();
                
                // 春季雨天概率 18.3%
                return chance < 0.183;
            }
        }
    }
}