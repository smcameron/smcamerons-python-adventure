#!/usr/bin/python
# This is a tiny little text adventure I'm writing in python
# for the purpose of learning python.
#
# -- steve
#
import re

# get the first item in a list


def get_first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default

# our player class, with a single instance, p, just has a location


class player:
    def __init__(self, location):
        self.location = location


class room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.visited = 0

    def describe(self):
        self.visited = 1
        print(self.description)


class thingy:
    def __init__(self, location, shortname, description, portable):
        self.shortname = shortname
        self.location = location
        self.description = description
        self.portable = portable


# Rooms
maintenance_room = room("Maintenance Room",
                        "You are in the maintenance room.  The floor is covered\n"
                        "in some kind of grungy substance.  A conrol panel is on the\n"
                        "wall.  A door leads out into a corridor to the south\n")
corridor = room("Corridor",
                "You are in a corridor.  To the east is the bridge.  To the\n"
                "west is the hold.  A doorway on the north side of the corridor\n"
                "leads into the maintenance room.\n")

maintenance_room.south = corridor
corridor.north = maintenance_room

pocket = room("pocket", "pocket")

# objects
knife = thingy(pocket, "knife", "a small pocket knife", 1)
mop = thingy(maintenance_room, "mop",  "a mop", 1)
bucket = thingy(maintenance_room, "bucket", "a bucket", 1)
control_panel = thingy(maintenance_room, "panel", "a control panel", 0)
substance = thingy(maintenance_room, "substance",
                   "some kind of grungy substance", 0)
substance.examine = "The grungy substance looks extremely unpleasant."

p = player(maintenance_room)

objects = {knife, mop, bucket, control_panel, substance}


def doquit(myobjs):
    print("Bye")
    exit()


def notimp(myobjects):
    print("not implemented")
    print("objects = ")
    print(myobjects)

#
# lookup a nown in the objects list, and return
# a list with 1st element being the text of the noun
# and 2nd being the matching element from objects list
# or None, if it wasn't found
#


def lookup_noun(noun):
    for o in objects:
        if (noun == o.shortname):
            return [noun, o]
    return [noun, None]


def lookup_nouns(nounlist):
    return map(lookup_noun, nounlist)

#
# this is for handling the word "all".
# lookup_nouns will translate "all" to
# [ "all", None ].  We want to replace
# that with the appropriate list of objects,
# The "appropriate" list is context sensitive.
# which for "drop", will be the list of objs
# that the player is carrying. for "take", will
# be the list of objects lying around.  For
# "examine", will be union of above two lists.
# Hence the fixupfunc, providing the context
# correct fixup function.
#


def fixup_all(objlist, fixupfunc):
    fixedup = []
    for x in objlist:
        if x[0] != "all":
            fixedup.append(x)
        else:
            fixedup.extend(fixupfunc())
    return fixedup

# turn an object from the object list into a list
# with first element == short name of object, second
# being the object.  For use with fixup functions for
# dealing with the word "all"
#


def makeobj(x):
    return [x.shortname, x]


def all_in_location(location):
    return [f for f in map(makeobj, objects) if f[1].location == location]


def all_in_room():
    return all_in_location(p.location)


def all_holding():
    return all_in_location(pocket)


def all_holding_or_here():
    return [f for f in map(makeobj, objects) if f[1].location == pocket or
            f[1].location == p.location]


def fixup_all_in_room(objlist):
    return fixup_all(objlist, all_in_room)


def fixup_all_holding(objlist):
    return fixup_all(objlist, all_holding)


def fixup_all_holding_or_here(objlist):
    return fixup_all(objlist, all_holding_or_here)


def lookup_nouns_fixup(nounlist, fixupfunc):
    objlist = lookup_nouns(nounlist)
    return fixupfunc(objlist)


def lookup_nouns_all_in_room(nounlist):
    return lookup_nouns_fixup(nounlist, fixup_all_in_room)


def lookup_nouns_all_holding(nounlist):
    return lookup_nouns_fixup(nounlist, fixup_all_holding)


def lookup_nouns_all_holding_or_here(nounlist):
    return lookup_nouns_fixup(nounlist, fixup_all_holding_or_here)


def doinventory(o):
    print("You are carrying:")
    for x in objects:
        if (x.location == pocket):
            print("  " + x.description)


def drop_object(o):
    w = o[0]
    obj = o[1]
    if obj == None:
        print(w + ": I don't know what that is.")
        return
    if obj.location != pocket:
        print(w + ": You do not have that.")
        return
    obj.location = p.location
    print(w + ": Dropped")


def take_object(o):
    w = o[0]
    obj = o[1]
    if obj == None:
        print(w + ": I don't know what that is.")
        return
    if obj.location != p.location:
        print(w + ": That is not here.")
        return
    if obj.portable != 1:
        print(w + ": You can't take that")
        return
    obj.location = pocket
    print(w + ": Taken.")
    return


def dodrop(words):
    todrop = lookup_nouns_all_holding(words)
    if not todrop:
        print("You need to tell me what to drop.")
        return
    map(drop_object, todrop)


def dotake(words):
    totake = lookup_nouns_all_in_room(words)
    if not totake:
        print("You need to tell me what to take.")
        return
    map(take_object, totake)


canonical_directions = ["north", "northeast", "east", "southeast", "south",
                        "southwest", "west", "northwest", "up", "down"]


def go_direction(direction):
    if (not hasattr(p.location, direction)):
        print(direction + ": You can't go that way.")
        return
    if (not direction in canonical_directions):
        print(direction + ": You can't go that way.")
        return
    destination = getattr(p.location, direction)
    if (not isinstance(destination, room)):
        print(direction + ": I don't understand.")
        return
    p.location = destination
    print("\n" + p.location.name + ":\n\n")


def dogo(words):
    map(go_direction, words)


def describe_obj_in_room(o):
    print("  " + o.description)


def describe_room(not_used):
    p.location.describe()
    print("You see:\n")
    objs_in_room = [f for f in objects if f.location == p.location]
    if not objs_in_room:
        print("  Nothing of interest.")
        return
    map(describe_obj_in_room, objs_in_room)


def examine_object(o):
    w = o[0]
    obj = o[1]
    if obj == None:
        print(w + ": I don't know what that is.")
        return
    if obj.location != pocket and obj.location != p.location:
        print(w + ": That is not here.")
        return
    if not hasattr(obj, "examine"):
        print(w + ": You see nothing special about that.")
        return
    print(obj.shortname + ": " + obj.examine)


def doexamine(words):
    tox = lookup_nouns_all_holding_or_here(words)
    if not tox:
        print("You need to tell me what to examine.")
        return
    map(examine_object, tox)


def dolisten(words):
    print("You hear the faint hum of space machinery.")


verbs = {
    'quit': doquit,
    'go': dogo,
    'take': dotake,
    'get': dotake,
    'drop': dodrop,
    'examine': doexamine,
    'x': doexamine,
    'look': describe_room,
    'inventory': doinventory,
    'i': doinventory,
    'listen': dolisten,
}

print("\n\n\n")
while 1:
    if (p.location.visited == 0):
        describe_room(1)
    words = re.split("[,; .]", raw_input("> "))
    first_word = get_first(words)
    if first_word in verbs:
        verbs[first_word](words[1:])
    else:
        print("Sorry, I don't know what that means.")
