def check_hemisphere(latitude):
    # The function checks the hemisphere of the ISS based on the given latitude
    if latitude > 0:
        print("Hello from the Northern Hemisphere!")
    else:
        print("Hello from the Southern Hemisphere!")
    
def get_relativity(speed):
    # The function prints the ISS's speed divided by the speed of light
    print("The ratio of the ISS speed to the speed of light is", speed/299792.458,".")
    
countdown = 5
while countdown > 0:    # The loop checks the hemisphere and relativity 5 times before ending
    check_hemisphere(-51.03)
    get_relativity(7.65)
    countdown -= 1
print("End")
