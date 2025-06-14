from typing import Dict, Optional


class Location:
    """
    Location representation class for Portuguese administrative divisions
    """
    
    def __init__(self, parish_id: int, parish_name: str, municipality_id: int, municipality_name: str, 
                 district_id: int, district_name: str, latitude: float = None, longitude: float = None):
        self._parish_id = parish_id
        self._parish_name = parish_name
        self._municipality_id = municipality_id
        self._municipality_name = municipality_name
        self._district_id = district_id
        self._district_name = district_name
        self._latitude = latitude
        self._longitude = longitude
    
    @property
    def parish_id(self) -> int:
        return self._parish_id
    
    @property
    def parish_name(self) -> str:
        return self._parish_name
    
    @property
    def municipality_id(self) -> int:
        return self._municipality_id
    
    @property
    def municipality_name(self) -> str:
        return self._municipality_name
    
    @property
    def district_id(self) -> int:
        return self._district_id
    
    @property
    def district_name(self) -> str:
        return self._district_name
    
    @property
    def latitude(self) -> Optional[float]:
        return self._latitude
    
    @property
    def longitude(self) -> Optional[float]:
        return self._longitude
    
    def set_coordinates(self, latitude: float, longitude: float):
        """Set location coordinates"""
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees")
        
        self._latitude = latitude
        self._longitude = longitude
    
    def has_coordinates(self) -> bool:
        """Check if location has valid coordinates"""
        return self._latitude is not None and self._longitude is not None
    
    def get_full_name(self) -> str:
        """Get complete location name"""
        return f"{self._parish_name}, {self._municipality_name}, {self._district_name}"
    
    def get_short_name(self) -> str:
        """Get short location name (parish + municipality)"""
        return f"{self._parish_name}, {self._municipality_name}"
    
    def is_complete(self) -> bool:
        """Check if location has all required data"""
        return all([
            self._parish_id,
            self._parish_name,
            self._municipality_id,
            self._municipality_name,
            self._district_id,
            self._district_name
        ])
    
    def to_dict(self) -> Dict:
        """Convert location to dictionary"""
        return {
            'parish': {
                'id': self._parish_id,
                'name': self._parish_name
            },
            'municipality': {
                'id': self._municipality_id,
                'name': self._municipality_name
            },
            'district': {
                'id': self._district_id,
                'name': self._district_name
            },
            'coordinates': {
                'latitude': self._latitude,
                'longitude': self._longitude
            } if self.has_coordinates() else None,
            'full_name': self.get_full_name(),
            'short_name': self.get_short_name(),
            'is_complete': self.is_complete()
        }
    
    @classmethod
    def from_hierarchy_data(cls, hierarchy_data: Dict) -> 'Location':
        """
        Create Location instance from hierarchy data
        
        Args:
            hierarchy_data: Dictionary with parish, municipality, district and coordinates
            
        Returns:
            Location instance
        """
        coords = hierarchy_data.get('coordinates', {})
        
        location = cls(
            parish_id=hierarchy_data['parish']['id'],
            parish_name=hierarchy_data['parish']['nome'],
            municipality_id=hierarchy_data['municipality']['id'],
            municipality_name=hierarchy_data['municipality']['nome'],
            district_id=hierarchy_data['district']['id'],
            district_name=hierarchy_data['district']['nome']
        )
        
        if coords.get('latitude') and coords.get('longitude'):
            location.set_coordinates(coords['latitude'], coords['longitude'])
        
        return location


class LocationHierarchy:
    """
    Helper class for managing hierarchical location selections
    """
    
    def __init__(self):
        self._selected_district = None
        self._selected_municipality = None
        self._selected_parish = None
        self._available_municipalities = []
        self._available_parishes = []
    
    @property
    def selected_district(self) -> Optional[Dict]:
        return self._selected_district
    
    @property
    def selected_municipality(self) -> Optional[Dict]:
        return self._selected_municipality
    
    @property
    def selected_parish(self) -> Optional[Dict]:
        return self._selected_parish
    
    @property
    def available_municipalities(self) -> list:
        return self._available_municipalities
    
    @property
    def available_parishes(self) -> list:
        return self._available_parishes
    
    def set_district(self, district: Dict, municipalities: list):
        """Set selected district and available municipalities"""
        self._selected_district = district
        self._available_municipalities = municipalities
        # Reset lower levels
        self._selected_municipality = None
        self._selected_parish = None
        self._available_parishes = []
    
    def set_municipality(self, municipality: Dict, parishes: list):
        """Set selected municipality and available parishes"""
        if not self._selected_district:
            raise ValueError("District must be selected first")
        
        self._selected_municipality = municipality
        self._available_parishes = parishes
        # Reset lower level
        self._selected_parish = None
    
    def set_parish(self, parish: Dict):
        """Set selected parish"""
        if not self._selected_municipality:
            raise ValueError("Municipality must be selected first")
        
        self._selected_parish = parish
    
    def is_complete(self) -> bool:
        """Check if hierarchy selection is complete"""
        return all([
            self._selected_district,
            self._selected_municipality,
            self._selected_parish
        ])
    
    def get_location(self) -> Optional[Location]:
        """Get Location object from current selection"""
        if not self.is_complete():
            return None
        
        return Location(
            parish_id=self._selected_parish['id'],
            parish_name=self._selected_parish['nome'],
            municipality_id=self._selected_municipality['id'],
            municipality_name=self._selected_municipality['nome'],
            district_id=self._selected_district['id'],
            district_name=self._selected_district['nome']
        )
    
    def reset(self):
        """Reset all selections"""
        self._selected_district = None
        self._selected_municipality = None
        self._selected_parish = None
        self._available_municipalities = []
        self._available_parishes = []
    
    def to_dict(self) -> Dict:
        """Convert hierarchy state to dictionary"""
        return {
            'selected_district': self._selected_district,
            'selected_municipality': self._selected_municipality,
            'selected_parish': self._selected_parish,
            'available_municipalities': self._available_municipalities,
            'available_parishes': self._available_parishes,
            'is_complete': self.is_complete()
        }