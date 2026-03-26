from core.area_utils import forward, back

def garden_gate(ctx, kwargs):
    print("You enter a clearing that appears to be home to a budding garden.")
    print("At the far side is a gate. Oddly a mist obscures seeing what is on the other side of it.")
    if not kwargs["first_time"]:
        print("You have been here before. You remember that the gate is locked from the other side.")
    print("Do you wish to pass through the gate?")
    print("1: Pass through the gate.")
    print("2: Turn back.")
    choice = input("What action do you take? (1-2): ")
    
    if choice == "1":
        return forward()
    elif choice == "2":
        print("You decide to turn back.")
        return back()

def back_of_gate(ctx, kwargs):
    if kwargs["entry_direction"] == "forward":
        print("You step through the gate, and it closes behind you.\n" \
        "A soft click is heard as it latches behind you.\n" \
        "The only way to go is forward.")
        return forward()
    else:
        print("You come to a garden gate. It is locked.\n" \
        "Unable to enter the garden, you are forced to turn back.")
        return back()