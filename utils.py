# File: utils.py

import random

def roll_dice(dice_notation):
    """
    Parses dice notation (e.g., '1d4+4') and returns the result of the roll.
    Supports notations like '1d4', '2d6+3', etc.
    """
    parts = dice_notation.split('+')
    dice_part = parts[0].split('d')
    num_dice = int(dice_part[0])  # Number of dice to roll (e.g., 1)
    dice_size = int(dice_part[1])  # Size of dice (e.g., 4 means a d4)
    
    # Roll the dice
    result = sum(random.randint(1, dice_size) for _ in range(num_dice))
    
    # Add modifier if applicable
    if len(parts) > 1:
        result += int(parts[1])  # Modifier (e.g., +4)

    return result
