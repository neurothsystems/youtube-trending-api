# services/config_manager.py - V6.0 Configuration Management
"""
V6.0 Configuration Management System
Zentralisierte Konfiguration für schnelle Algorithmus-Anpassungen
"""

import os
import yaml
import json
import configparser
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class MomentumConfig:
    """MOMENTUM Algorithm Configuration"""
    velocity_weight: float = 0.6
    engagement_weight: float = 0.3
    freshness_weight: float = 0.1
    time_decay_hours: float = 24.0
    trending_page_bonus: float = 1.5


@dataclass
class RegionalConfig:
    """Regional Filter Configuration"""
    max_asian_videos: int = 1
    german_boost_factor: float = 0.4
    anti_bias_threshold: float = 0.35
    spam_detection_threshold: float = 0.5


@dataclass
class ScraperConfig:
    """Trending Scraper Configuration"""
    request_timeout: int = 15
    max_retries: int = 3
    delay_between_requests: float = 1.0
    use_cache: bool = True
    cache_ttl: int = 300


@dataclass
class V6Config:
    """Complete V6.0 Configuration"""
    momentum: MomentumConfig
    regional: RegionalConfig
    scraper: ScraperConfig
    default_region: str = "DE"
    api_key: Optional[str] = None
    supported_regions: list = None
    
    def __post_init__(self):
        if self.supported_regions is None:
            self.supported_regions = ['DE', 'US', 'GB', 'FR', 'ES', 'IT', 'AT', 'CH', 'NL']


class ConfigManager:
    """V6.0 Configuration Manager"""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize Configuration Manager
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Default configuration
        self._default_config = V6Config(
            momentum=MomentumConfig(),
            regional=RegionalConfig(),
            scraper=ScraperConfig()
        )
        
        # Current active configuration
        self.config = self._load_config()
        
        print(f"🔧 V6.0 Config Manager initialized")
        print(f"   Config directory: {self.config_dir}")
        print(f"   Default region: {self.config.default_region}")
    
    def _load_config(self) -> V6Config:
        """Load configuration from files"""
        try:
            # Try to load from YAML first (preferred)
            yaml_path = self.config_dir / "v6_config.yaml"
            if yaml_path.exists():
                return self._load_from_yaml(yaml_path)
            
            # Fallback to legacy config.ini
            ini_path = self.config_dir / "config.ini"
            legacy_path = Path("config.ini")
            
            if ini_path.exists():
                return self._load_from_ini(ini_path)
            elif legacy_path.exists():
                return self._load_from_ini(legacy_path)
            
            # Use defaults and create config file
            self._create_default_config_files()
            return self._default_config
            
        except Exception as e:
            print(f"⚠️  Config load error: {e}, using defaults")
            return self._default_config
    
    def _load_from_yaml(self, path: Path) -> V6Config:
        """Load configuration from YAML file"""
        print(f"📄 Loading config from: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Parse sections
        momentum_config = MomentumConfig(**data.get('momentum', {}))
        regional_config = RegionalConfig(**data.get('regional', {}))
        scraper_config = ScraperConfig(**data.get('scraper', {}))
        
        # Get API key from environment or file
        api_key = os.getenv('YOUTUBE_API_KEY') or data.get('api_key')
        
        return V6Config(
            momentum=momentum_config,
            regional=regional_config,
            scraper=scraper_config,
            default_region=data.get('default_region', 'DE'),
            api_key=api_key,
            supported_regions=data.get('supported_regions')
        )
    
    def _load_from_ini(self, path: Path) -> V6Config:
        """Load configuration from legacy INI file"""
        print(f"📄 Loading legacy config from: {path}")
        
        config = configparser.ConfigParser()
        config.read(path)
        
        # Extract API key
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key and config.has_option('API', 'api_key'):
            api_key = config.get('API', 'api_key')
        
        # Parse MOMENTUM settings (from TRENDING section)
        momentum_config = MomentumConfig()
        if config.has_section('TRENDING'):
            # Map legacy settings to new structure
            if config.has_option('TRENDING', 'engagement_factor'):
                # Legacy: higher engagement_factor = higher engagement weight
                engagement_factor = config.getfloat('TRENDING', 'engagement_factor', fallback=10.0)
                momentum_config.engagement_weight = min(0.4, engagement_factor / 30.0)
            
            if config.has_option('TRENDING', 'freshness_exponent'):
                # Legacy: higher exponent = faster decay
                freshness_exp = config.getfloat('TRENDING', 'freshness_exponent', fallback=1.3)
                momentum_config.time_decay_hours = 24.0 / freshness_exp
        
        # Parse regional settings (use defaults mostly)
        regional_config = RegionalConfig()
        
        # Parse scraper settings
        scraper_config = ScraperConfig()
        
        return V6Config(
            momentum=momentum_config,
            regional=regional_config,
            scraper=scraper_config,
            api_key=api_key
        )
    
    def _create_default_config_files(self):
        """Create default configuration files"""
        print("📝 Creating default configuration files...")
        
        # Create YAML config
        yaml_path = self.config_dir / "v6_config.yaml"
        yaml_content = {
            'default_region': 'DE',
            'supported_regions': ['DE', 'US', 'GB', 'FR', 'ES', 'IT', 'AT', 'CH', 'NL'],
            'api_key': None,  # Set via environment variable
            
            'momentum': asdict(self._default_config.momentum),
            'regional': asdict(self._default_config.regional),
            'scraper': asdict(self._default_config.scraper)
        }
        
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)
        
        # Create example environment file
        env_path = self.config_dir / ".env.example"
        with open(env_path, 'w') as f:
            f.write("# V6.0 Environment Variables\n")
            f.write("YOUTUBE_API_KEY=your_youtube_api_key_here\n")
            f.write("V6_DEFAULT_REGION=DE\n")
            f.write("V6_CACHE_ENABLED=true\n")
        
        print(f"✅ Created: {yaml_path}")
        print(f"✅ Created: {env_path}")
    
    def get_momentum_config(self) -> MomentumConfig:
        """Get MOMENTUM algorithm configuration"""
        return self.config.momentum
    
    def get_regional_config(self, region: str = None) -> RegionalConfig:
        """Get regional filter configuration for specific region"""
        # Could be extended to have region-specific settings
        return self.config.regional
    
    def get_scraper_config(self) -> ScraperConfig:
        """Get trending scraper configuration"""
        return self.config.scraper
    
    def get_api_key(self) -> Optional[str]:
        """Get YouTube API key"""
        # Try environment first, then config
        return os.getenv('YOUTUBE_API_KEY') or self.config.api_key
    
    def get_supported_regions(self) -> list:
        """Get list of supported regions"""
        return self.config.supported_regions
    
    def update_momentum_config(self, **kwargs):
        """Update MOMENTUM algorithm configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.momentum, key):
                setattr(self.config.momentum, key, value)
                print(f"🔧 Updated momentum.{key} = {value}")
        
        self._save_config()
    
    def update_regional_config(self, **kwargs):
        """Update regional filter configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.regional, key):
                setattr(self.config.regional, key, value)
                print(f"🔧 Updated regional.{key} = {value}")
        
        self._save_config()
    
    def update_scraper_config(self, **kwargs):
        """Update scraper configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.scraper, key):
                setattr(self.config.scraper, key, value)
                print(f"🔧 Updated scraper.{key} = {value}")
        
        self._save_config()
    
    def _save_config(self):
        """Save current configuration to YAML file"""
        try:
            yaml_path = self.config_dir / "v6_config.yaml"
            
            config_data = {
                'default_region': self.config.default_region,
                'supported_regions': self.config.supported_regions,
                'momentum': asdict(self.config.momentum),
                'regional': asdict(self.config.regional),
                'scraper': asdict(self.config.scraper)
            }
            
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
            
            print(f"💾 Config saved to: {yaml_path}")
            
        except Exception as e:
            print(f"⚠️  Error saving config: {e}")
    
    def get_algorithm_presets(self) -> Dict[str, MomentumConfig]:
        """Get predefined algorithm presets"""
        return {
            'balanced': MomentumConfig(
                velocity_weight=0.6,
                engagement_weight=0.3,
                freshness_weight=0.1,
                trending_page_bonus=1.5
            ),
            'velocity_focused': MomentumConfig(
                velocity_weight=0.8,
                engagement_weight=0.15,
                freshness_weight=0.05,
                trending_page_bonus=1.3
            ),
            'engagement_focused': MomentumConfig(
                velocity_weight=0.4,
                engagement_weight=0.5,
                freshness_weight=0.1,
                trending_page_bonus=1.7
            ),
            'anti_spam': MomentumConfig(
                velocity_weight=0.7,
                engagement_weight=0.2,
                freshness_weight=0.1,
                time_decay_hours=12.0,
                trending_page_bonus=1.8
            )
        }
    
    def apply_preset(self, preset_name: str):
        """Apply predefined configuration preset"""
        presets = self.get_algorithm_presets()
        
        if preset_name not in presets:
            available = ', '.join(presets.keys())
            raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")
        
        self.config.momentum = presets[preset_name]
        self._save_config()
        
        print(f"✅ Applied preset: {preset_name}")
        print(f"   Velocity: {self.config.momentum.velocity_weight}")
        print(f"   Engagement: {self.config.momentum.engagement_weight}")
        print(f"   Freshness: {self.config.momentum.freshness_weight}")
        print(f"   Trending Bonus: {self.config.momentum.trending_page_bonus}")
    
    def export_config(self, format: str = 'json') -> str:
        """Export current configuration"""
        config_dict = {
            'default_region': self.config.default_region,
            'supported_regions': self.config.supported_regions,
            'momentum': asdict(self.config.momentum),
            'regional': asdict(self.config.regional),
            'scraper': asdict(self.config.scraper),
            'export_timestamp': str(datetime.now()),
            'version': 'V6.0'
        }
        
        if format.lower() == 'json':
            return json.dumps(config_dict, indent=2)
        elif format.lower() == 'yaml':
            return yaml.dump(config_dict, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for API"""
        return {
            'version': 'V6.0',
            'default_region': self.config.default_region,
            'supported_regions': len(self.config.supported_regions),
            'api_key_configured': bool(self.get_api_key()),
            'momentum_algorithm': {
                'velocity_weight': self.config.momentum.velocity_weight,
                'engagement_weight': self.config.momentum.engagement_weight,
                'freshness_weight': self.config.momentum.freshness_weight,
                'trending_page_bonus': f"+{(self.config.momentum.trending_page_bonus-1)*100:.0f}%"
            },
            'regional_filter': {
                'max_asian_videos': self.config.regional.max_asian_videos,
                'german_boost_factor': f"+{self.config.regional.german_boost_factor*100:.0f}%",
                'anti_bias_enabled': True
            },
            'scraper': {
                'cache_enabled': self.config.scraper.use_cache,
                'cache_ttl_minutes': self.config.scraper.cache_ttl // 60,
                'request_timeout': f"{self.config.scraper.request_timeout}s"
            },
            'available_presets': list(self.get_algorithm_presets().keys())
        }


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_momentum_config() -> MomentumConfig:
    """Convenience function to get MOMENTUM config"""
    return get_config_manager().get_momentum_config()


def get_regional_config(region: str = None) -> RegionalConfig:
    """Convenience function to get regional config"""
    return get_config_manager().get_regional_config(region)


def get_scraper_config() -> ScraperConfig:
    """Convenience function to get scraper config"""
    return get_config_manager().get_scraper_config()


# Test function
if __name__ == "__main__":
    from datetime import datetime
    
    print("🧪 V6.0 Configuration Manager Test")
    print("=" * 50)
    
    # Initialize config manager
    config_mgr = ConfigManager()
    
    # Test configuration access
    momentum_cfg = config_mgr.get_momentum_config()
    print(f"📊 MOMENTUM Config:")
    print(f"   Velocity Weight: {momentum_cfg.velocity_weight}")
    print(f"   Engagement Weight: {momentum_cfg.engagement_weight}")
    print(f"   Trending Bonus: +{(momentum_cfg.trending_page_bonus-1)*100:.0f}%")
    
    regional_cfg = config_mgr.get_regional_config()
    print(f"\n🌍 Regional Config:")
    print(f"   Max Asian Videos: {regional_cfg.max_asian_videos}")
    print(f"   German Boost: +{regional_cfg.german_boost_factor*100:.0f}%")
    
    # Test presets
    print(f"\n🎛️  Available Presets:")
    presets = config_mgr.get_algorithm_presets()
    for name, preset in presets.items():
        print(f"   {name}: velocity={preset.velocity_weight}, engagement={preset.engagement_weight}")
    
    # Test configuration update
    print(f"\n🔧 Testing configuration update...")
    config_mgr.update_momentum_config(velocity_weight=0.7, engagement_weight=0.25)
    
    # Test summary
    print(f"\n📋 Configuration Summary:")
    summary = config_mgr.get_config_summary()
    print(json.dumps(summary, indent=2))
