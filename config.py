#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration script - Unified management of map generation and heatmap generation
Supports multiple region name display modes and batch processing
"""

import sys
import os
import subprocess
from datetime import datetime

def print_banner():
    """Print program banner"""
    print("=" * 70)
    print("Area Data Visualization Tool v2.0")
    print("=" * 70)
    print("Functions:")
    print("  Map Generation (map.py) - Multiple region name display modes")
    print("  Heatmap Generation (heatmap.py) - Customer churn rate heatmap")
    print("=" * 70)

def print_menu():
    """Print menu options"""
    print("\nPlease select running mode:")
    print("1. Generate map - Show all region names")
    print("2. Generate map - Show partial region names (data regions only)")
    print("3. Generate map - Hide all region names")
    print("4. Generate heatmap")
    print("5. Generate customer churn analysis report")
    print("6. Generate all 3 map modes + heatmap")
    print("7. Generate all 3 map modes + heatmap + analysis report")
    print("8. Custom mode selection")
    print("0. Exit")
    print("-" * 50)

def run_map_generation(display_modes):
    """Run map generation"""
    print(f"\nStarting map generation, mode: {display_modes}")
    
    try:
        # Import map module and run
        import map as map_module
        
        # Determine run mode based on number of modes
        if len(display_modes) == 1:
            run_mode = 'single'
        elif len(display_modes) == 3 and set(display_modes) == {'all', 'partial', 'none'}:
            run_mode = 'all'
        else:
            run_mode = 'multiple'
        
        # Run map generation
        results = map_module.main(run_mode=run_mode, display_modes=display_modes)
        
        print("Map generation completed!")
        return True
        
    except Exception as e:
        print(f"Map generation failed: {e}")
        return False

def run_heatmap_generation():
    """Run heatmap generation"""
    print("\nStarting heatmap generation...")
    
    try:
        # Import heatmap module and run
        import heatmap as heatmap_module
        
        # Run heatmap generation
        success = heatmap_module.create_heatmap()
        
        if success:
            print("Heatmap generation completed!")
            return True
        else:
            print("Heatmap generation failed")
            return False
        
    except Exception as e:
        print(f"Heatmap generation failed: {e}")
        return False

def run_analysis_report_generation():
    """Run analysis report generation"""
    print("\nStarting analysis report generation...")
    
    try:
        # Import heatmap module and run analysis report function
        import heatmap as heatmap_module
        
        # Run analysis report generation
        success = heatmap_module.generate_analysis_report()
        
        if success:
            print("Analysis report generation completed!")
            print("Report file saved: 流失率分析报告.txt")
            return True
        else:
            print("Analysis report generation failed")
            return False
        
    except Exception as e:
        print(f"Analysis report generation failed: {e}")
        return False

def get_custom_modes():
    """Get custom mode selection"""
    print("\nCustom mode selection")
    print("Available modes:")
    print("  all - Show all region names")
    print("  partial - Show partial region names (data regions only)")
    print("  none - Hide all region names")
    
    modes = []
    mode_mapping = {
        'a': 'all',
        'p': 'partial', 
        'n': 'none'
    }
    
    while True:
        choice = input("Enter mode code (a/p/n), multiple modes separated by space, or 'done' to finish selection: ").strip().lower()
        
        if choice == 'done':
            break
        elif choice == 'all':
            modes = ['all', 'partial', 'none']
            break
        
        selected_modes = choice.split()
        for mode_code in selected_modes:
            if mode_code in mode_mapping:
                mode = mode_mapping[mode_code]
                if mode not in modes:
                    modes.append(mode)
                    print(f"  Selected: {mode}")
            else:
                print(f"  Invalid code: {mode_code}")
    
    return modes if modes else ['partial']

def main():
    """Main program"""
    print_banner()
    
    while True:
        print_menu()
        
        try:
            choice = input("Enter option (0-8): ").strip()
            
            if choice == '0':
                print("Goodbye!")
                break
                
            elif choice == '1':
                # Show all region names
                run_map_generation(['all'])
                
            elif choice == '2':
                # Show partial region names
                run_map_generation(['partial'])
                
            elif choice == '3':
                # Hide all region names
                run_map_generation(['none'])
                
            elif choice == '4':
                # Generate heatmap
                run_heatmap_generation()
                
            elif choice == '5':
                # Generate analysis report
                run_analysis_report_generation()
                
            elif choice == '6':
                # Generate all modes
                print("\nStarting all mode generation...")
                
                # Generate all 3 map modes
                map_success = run_map_generation(['all', 'partial', 'none'])
                
                # Generate heatmap
                heatmap_success = run_heatmap_generation()
                
                if map_success and heatmap_success:
                    print("\nAll tasks completed!")
                    print("File save location:")
                    print("  - Map files: map_outputs/")
                    print("    - all/ (show all region names)")
                    print("    - partial/ (show partial region names)")  
                    print("    - none/ (hide all region names)")
                    print("  - Heatmap file: heatmap_output/")
                else:
                    print("Some tasks failed, please check error message")
                
            elif choice == '7':
                # Generate all modes + analysis report
                print("\nStarting all mode generation...")
                
                # Generate all 3 map modes
                map_success = run_map_generation(['all', 'partial', 'none'])
                
                # Generate heatmap
                heatmap_success = run_heatmap_generation()
                
                # Generate analysis report
                analysis_report_success = run_analysis_report_generation()
                
                if map_success and heatmap_success and analysis_report_success:
                    print("\nAll tasks completed!")
                    print("File save location:")
                    print("  - Map files: map_outputs/")
                    print("    - all/ (show all region names)")
                    print("    - partial/ (show partial region names)")  
                    print("    - none/ (hide all region names)")
                    print("  - Heatmap file: heatmap_output/")
                    print("  - Analysis report file: 流失率分析报告.txt")
                else:
                    print("Some tasks failed, please check error message")
                
            elif choice == '8':
                # Custom mode selection
                custom_modes = get_custom_modes()
                if custom_modes:
                    run_map_generation(custom_modes)
                    
                    # Ask if generate heatmap
                    heatmap_choice = input("\nGenerate heatmap? (y/n): ").strip().lower()
                    if heatmap_choice in ['y', 'yes', '是']:
                        run_heatmap_generation()
                        
                    # Ask if generate analysis report
                    analysis_report_choice = input("\nGenerate analysis report? (y/n): ").strip().lower()
                    if analysis_report_choice in ['y', 'yes', '是']:
                        run_analysis_report_generation()
                
            else:
                print("Invalid option, please re-select")
                
        except KeyboardInterrupt:
            print("\n\nUser cancelled operation, goodbye!")
            break
        except EOFError:
            print("\n\nInput ended, goodbye!")
            break
        except Exception as e:
            print(f"Program execution error: {e}")
            choice = ''  # 设置默认值避免后续错误
        
        # Ask if continue
        if choice != '0':
            try:
                continue_choice = input("\nContinue using? (y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes', '是', '']:
                    print("Goodbye!")
                    break
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break

if __name__ == "__main__":
    main()
