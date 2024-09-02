directions = {'N','NE','E','SE','S','SW','W','NW'}
def getDirection(myCoords:tuple ,otherCoords:tuple):
    myX, myY = myCoords
    otherX, otherY = otherCoords
    if otherX < myX:
        if otherY < myY:
            return 'NW'
        elif otherY == myY:
            return 'N'
        else:
            return 'NE'
    elif otherX == myX:
        if otherY < myY:
            return 'O'
        elif otherY == myY:
            return None
        else:
            return 'E'
    else:
        if otherY < myY:
            return 'SW'
        elif otherY == myY:
            return 'S'
        else:
            return 'SE'

def getOppositeDirection(myCoords:tuple, otherCoords:tuple):
    return getDirection(otherCoords, myCoords)

print(getDirection((3,3),(3,1)), getOppositeDirection((3,3),(3,1)))