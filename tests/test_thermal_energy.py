#!/usr/bin/env python3
"""
Simple test script for thermal energy parsing functionality.
"""
import sys
import os

# Add the eaip_full_skeleton to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'eaip_full_skeleton'))

try:
    from services.ingest.utils.energy_aggregator import aggregate_single_resource_file  # type: ignore
except ImportError:
    # Fallback for when running from different directory
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "energy_aggregator",
        os.path.join(os.path.dirname(__file__), 'eaip_full_skeleton', 'services', 'ingest', 'utils', 'energy_aggregator.py')
    )
    energy_aggregator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(energy_aggregator)
    aggregate_single_resource_file = energy_aggregator.aggregate_single_resource_file

def test_thermal_energy_parsing():
    print('🧪 Testing thermal energy parsing...')

    test_file = 'data/source_files/audit_sinergys/otoplenie.xlsx'
    if os.path.exists(test_file):
        print(f'✅ Found test file: {test_file}')
        try:
            result = aggregate_single_resource_file(test_file)
            if result and 'resources' in result and 'heat' in result['resources']:
                print('✅ Thermal energy parsing works!')
                heat_data = result['resources']['heat']
                print(f'📊 Found {len(heat_data)} quarters of thermal data')
                for quarter_key, quarter_data in heat_data.items():
                    months = len(quarter_data.get('months', []))
                    print(f'  📅 {quarter_key}: {months} months')
                return True
            else:
                print('❌ Thermal energy parsing failed or returned building data')
                if result and 'buildings' in result:
                    print('📋 Returned building inventory instead of consumption data')
                    buildings = result.get('buildings', [])
                    print(f'🏢 Found {len(buildings)} buildings')
                else:
                    print(f'📄 Result structure: {list(result.keys()) if result else "None"}')
                return False
        except Exception as e:
            print(f'❌ Error testing thermal energy: {e}')
            import traceback
            traceback.print_exc()
            return False
    else:
        print(f'❌ Test file not found: {test_file}')
        print('📁 Available files in audit_sinergys:')
        audit_dir = 'data/source_files/audit_sinergys'
        if os.path.exists(audit_dir):
            files = [f for f in os.listdir(audit_dir) if f.endswith('.xlsx')]
            for f in files:
                print(f'  📄 {f}')
        return False

if __name__ == '__main__':
    success = test_thermal_energy_parsing()
    print(f'\n🎯 Test result: {"PASSED" if success else "FAILED"}')
