# PathfinderEncounterTracker
 
I want to have it so that I can keep track of Larger encounters a little easier - including Ones with slightly different events (the large scale battle style as well)

I'll put it in a GUI I think so that I can use it simpler on the fly. 

There will be a samplefile with some of everything I think. 

Design:
    Creature/Army - This will be the referral
        Key: Value

Keys:
-------- Shared ---------
    Name: String - Just to View
    CR: Int
    Stats: Dictionary - each has a way to roll it
        Keys: STR INT WIS DEX CHA CON Reflex Fortitude Wisdom  -> Int
    MaxHp: Int - Const
    CurrentHp: Int - Modifiable - Means something slightly different for Army
    Notes: String - Button to display it I think
    Description: String

--------- Monster Specific -------
    Attack: Class - Callable calls the DamageRoll
        Weapon: String (Weapon Type/Name of weapon)
        MeleeRanged: Set(Melee, Ranged)
        Range: Int (in feet)
        Type: Set(Bludgeoning, Piercing, Slashing)
        DamageRoll: Object and Callable 
            Value: String - What to roll for the damage and the like
    AC: Int
    
--------- Army Specific -----------
    ArmyKills: Class - Callable - Takes Int 
        Bonus: Int (Typically just CR - Will default that if not specified)
        BaseDamageMultiplier: Int (How much to multiply the Damage) 


Army Specific Calculation:
    Roll d20 Add Bonus Subtract Opponents Bonus = BASE
    Take BaseDamageMultiplier and Subtract it by opponents BaseDamageMultiplier (MIN 1) as MULT
    Should make it so that can give name, or 
    DAMAGE = BASE * MULT (Where Randomly between 10 and 20% are injured rather than dead)

Monster Attack will just Roll the Attack (Full Attack Assumed) with Damage beside each (With the breakdown in case of crit - won't manually calculate it)


So for each monster attack defined needs to create a button to do it
Technically as well for the Kills

Also need to have a save button/Save as button

Start of program -> choose file to load (or use in the arguments)

# TODO
Add Resistances, and make it so that the Damage takes this into account
Add Variables to Attack Bonus
