"""
FarmVille - AI-Powered Agro Assistant
"""

from services.weather_service import WeatherService

def main():
    print("🌾 FarmVille - AI-Powered Agro Assistant")
    print("=" * 60)
    
    weather_service = WeatherService()
    
    print("\n📍 Testing single location:")
    porto_weather = weather_service.get_weather_data("Porto, Portugal", 41.1579, -8.6291)
    print(porto_weather)
    
    print("\n📍 Testing multiple locations:")
    locations = [
        ("Lisboa, Portugal", 38.7223, -9.1393),
        ("Madrid, Spain", 40.4168, -3.7038),
        ("Paris, France", 48.8566, 2.3522)
    ]
    
    weather_data_list = weather_service.get_multiple_locations(locations)
    
    for weather in weather_data_list:
        print(f"  • {weather}")
    
    print("\n💾 Testing cache functionality:")
    print("Cache info:", weather_service.get_cache_info())
    
    print("\n🔄 Second call to Porto (should use cache):")
    porto_weather_cached = weather_service.get_weather_data("Porto, Portugal", 41.1579, -8.6291)
    print(porto_weather_cached)
    
    print("\n✅ Weather Service test completed!")

if __name__ == "__main__":
    main()