import space_controller
import random
import time
import threading
import signal
import sys

simulation_running = True
battery_lock = threading.Lock()
ledDisplayObject = None

def signal_handler(signum, frame):
    global simulation_running
    print("Stopping simulation...")
    simulation_running = False

def battery_discharge_simulation():
    global simulation_running
    current_battery = 75
    
    print("Starting battery discharge simulation...")
    print("Press Ctrl+C to stop the simulation")
    
    while simulation_running and current_battery > 0:
        try:
            tickRate = 1.0
            random_tick_speed = random.uniform(0.5, 3.0) * tickRate
            battery_decrease = random.randint(1, 5)
            
            with battery_lock:
                current_battery = max(0, current_battery - battery_decrease)
                ledDisplayObject.setBatteryLevel(current_battery)
            
            print(f"Tick: {random_tick_speed:.2f}s | Battery decreased by {battery_decrease}% | Current: {current_battery}%")
            ledDisplayObject.updateLedStates()
            
            time.sleep(random_tick_speed)
            
        except space_controller.LEDDisplayError as e:
            print(f"LED Display error: {e}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    
    print("Battery simulation completed!")

def main():
    global simulation_running, ledDisplayObject
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        with space_controller.LEDDisplay(
            batteryInput=100, 
            ledPinsArrStatus=[0]*10, 
            ledPinsArr=[4, 5, 6, 12, 13, 16, 17, 18, 19, 20]
        ) as ledDisplayObject:
            
            print("LED Display initialized successfully")
            
            ledDisplayObject.calculateLedStates()
            ledDisplayObject.updateLedStates()
            print("Initial state set")
            
            battery_thread = threading.Thread(target=battery_discharge_simulation)
            battery_thread.daemon = True
            battery_thread.start()
            
            while simulation_running and battery_thread.is_alive():
                time.sleep(0.1)
            
            if battery_thread.is_alive():
                print("Waiting for simulation thread to finish...")
                battery_thread.join(timeout=5.0)
            
    except space_controller.LEDDisplayError as e:
        print(f"LED Display initialization failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        print("Simulation ended")

if __name__ == "__main__":
    main()
