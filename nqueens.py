import numpy as np
import random

def nqueens():
    size_list = []
    f = open("nqueens.txt", "r")
    f_out = open("nqueens_out.txt", "w")

    #get board sizes from "nqueens.txt"
    for i in f:
        size_list.append(int(i))

    for j in size_list:
        success = False
        while not success:
            solution = Board(j) #creating an instance of our class to solve the solution
            success = solution.solve() #calling the function that solves the initial placement of queens
            #print(success)
        tempL = solution.getSol()
        f_out.write("[")
        for t in tempL[:-1]:
            f_out.write("%d," % t)
        f_out.write("%d" % tempL[-1])
        f_out.write("]\n")
        
class Board:
    def __init__(self,numQ): #Constructor that takes argument numQ. numQ is the number of queens we must place
        self.numQ = numQ #numQ variable assignment 
        self.row = np.empty(self.numQ, dtype=int) #creating an empty numpy array of ints. we use numpy because this array initialization method is around x10 faster than regular python methods
        self.col = [set() for _ in range(self.numQ)] #we maintain a set of arrays for columns to keep lookups in O(1). If 2 queens are in the same column, they will be in the same set. the index of the col array denotes the column, and the value(s) is/are the row(s)
        self.leftD = [ set() for _ in range(2*self.numQ-1) ] #same concept as columns but with left diagonals (refer to the drawing in the chat)
        self.rightD = [ set() for _ in range(2*self.numQ-1) ] #same concept as leftD but opposite direction
        self.realSize = self.numQ - 1 #actual size used for index and random number calculations
        self.emptyCol = { c for c in range(numQ) } #set of empty columns used for many purposes, purposes will be outlined per lin
        placed = 0 #variable for calculating how many queens we were able to place randomly without conflicts
        last = True
        self.emptyCols = list(self.emptyCol)
        i = 0
        #trying to place a queen with 0-conflicts 5*numQ, then we place the remaining queens randomly
        for _ in range(5*numQ):
            if self.emptyCols:
                randIndex = random.randint(0, len(self.emptyCols) -1)
                randCol = self.emptyCols[randIndex]
                if(self.getConflicts(i, randCol) + 3 == 0):
                    self.emptyCol.remove(randCol) #removing the column from the set of empty columns
                    self.row[i] = randCol #setting the row value to the column. remember, the index denotes the row and the value denotes which column it's in
                    self.col[randCol].add(i) #setting the col at index randCol to the row index
                    self.leftD[self.realSize - (i - randCol)].add(randCol if (i > randCol) else i) #setting the left diagonal. index calculations were explained in our meeting
                    self.rightD[2*self.realSize - (i + randCol)].add((self.realSize - randCol) if ((i + randCol) >= self.realSize) else i) #setting the right diagonal. index calculations were explained in our meeting
                    self.removeFromList(randIndex)
                    i += 1
                    placed += 1
                
        while (i < numQ): #we place a queen each row. i is the row index.
            randIndex = random.randint(0, len(self.emptyCols) -1)
            randCol = self.emptyCols[randIndex]
            if randCol in self.emptyCol: #keyerror check
                self.emptyCol.remove(randCol) #removing the column from the set of empty columns
                self.row[i] = randCol #literally the same code as above
                self.col[randCol].add(i)
                self.leftD[self.realSize - (i - randCol)].add(randCol if (i > randCol) else i)
                self.rightD[2*self.realSize - (i + randCol)].add((self.realSize - randCol) if ((i + randCol) >= self.realSize) else i)
                i += 1
                self.removeFromList(randIndex)
        #print("Done Initializing")
        #print(placed)#printing out the number of 0-conflict queens we were able to place randomly, use this to generate cool statistics!
    

    def removeFromList(self, index):
        temp = self.emptyCols[len(self.emptyCols) - 1]
        self.emptyCols[index] = temp
        self.emptyCols[len(self.emptyCols) - 1] = None
        self.emptyCols.pop()
        
        
    def getConflicts(self,r,c): #this function gets the conflicts of a square. the reason it subtracts 3 is because I first designed this function to check the conflicts of a given queen, and since each queen may have conflicts in 3 arrays (remember we only ever have one queen per row) we subtract 3.
        return len(self.col[c]) + len(self.leftD[self.realSize - (r - c)]) + len(self.rightD[2*self.realSize - (r + c)]) - 3

    #returns the rows in which the maximums are found
    def getMostConflicting(self): #returns the index of the queen with the most conflicts. if there are multiple, it returns an array of the indices. If this function returns an empty array, the board is solved.
        maxConflicts = 0 #var for the maximum conflicts we encounter
        indicesOfMax = [] #array to store the indices of the max conflicts
        for j in range(self.numQ): #iterating through each queen
            if(self.getConflicts(j,self.row[j]) > maxConflicts): #if the queen at row j has more conflicts than max conflicts, then clear the array, and add the index to the array
                maxConflicts = self.getConflicts(j,self.row[j]) #setting the maxConflicts variable to the conflicts of queen at row j.
                indicesOfMax.clear()
                indicesOfMax.append(j)
            elif(self.getConflicts(j,self.row[j]) == maxConflicts and maxConflicts > 0): #if the conflicts at row j is equal to maxConflicts, we append it to the array. second argument in the if statement ensure we return an empty array when the board is solved
                indicesOfMax.append(j)
        return indicesOfMax #returning the indices of the rows of the maximum conflicting queens

    def solve(self):
        options = self.getMostConflicting() #the options of queens to move
        tMoves = 0
        while(options): #while the options array isn't empty
            rQueen = options[random.randint(0,(len(options) -1))] #row index of random queen in options (remember, if len(options) > 1 that means more than one queen have the same number of conflicts that are the maximum conflicts
            placedInEmpty = False #var to keep track of if we placed a queen in an 0-conflict square
            if self.emptyCol: #if there are any empty columns
                e = None #e is a variable used to iterate through the empty set. if we don't set it to none, next time we call this it will start iterating through emptyCol from the previous e
                for e in self.emptyCol: #iterating through the empty set
                    if((self.getConflicts(rQueen, e) + 3) == 0): #if we find a 0-conflict square
                        self.update(rQueen, self.row[rQueen], e) #move it to the 0-conflict square
                        placedInEmpty = True #we found a 0-conflict square!
                        break #break out of the for loop
            if not placedInEmpty: #if we didn't find a 0-conflict square :(
                found = False #variable for if we find a 1-conflict square
                for _ in range(25): #we try 25 times (ask me about this for why I chose 25)
                    randColInRow = random.randint(0, self.realSize) #we try a random col in the row
                    if (randColInRow != self.row[rQueen]): #if the randCol we generated isn't the col the queen we are trying to move is in
                        if ((self.getConflicts(rQueen, randColInRow) + 3) == 1): #if the square is a 1-conflict square
                            self.update(rQueen, self.row[rQueen], randColInRow) #move it to this 1-conflict square
                            found = True #we found a 1-conflict square!
                            break #break out of the for loop
                if not found: #if we didn't find a 1-conflict square :(
                    minConflicts = self.numQ #variable to keep track of the min-conflicts of the row
                    indicesOfMin = [] #array to keep track of the indices of the columns with the minimun amount of conflicts.
                    for k in range(self.numQ): #iterate through the row
                        if(k != self.row[rQueen]): #if the current col is not the one with a queen on it
                            if(self.getConflicts(rQueen,k) + 3 < minConflicts): #if the number of conflicts is less than minConflicts, clear the array and append the index and update minConflicts
                                minConflicts = self.getConflicts(rQueen,k) + 3
                                indicesOfMin.clear()
                                indicesOfMin.append(k)
                            elif(self.getConflicts(rQueen,k) + 3 == minConflicts): #if it's equal, just append to the array
                                indicesOfMin.append(k)
                    cQueen = indicesOfMin[random.randint(0, (len(indicesOfMin) - 1))] #column of min index square
                    self.update(rQueen, self.row[rQueen], cQueen) #move queen to this square
            options = self.getMostConflicting() #refresh our options
            tMoves += 1
            if(tMoves > 100*self.numQ):
                return False
        return True
        #print(self.printArr())
            

    def update(self,sRow, sCol, fCol): #our move-to function.
        if(len(self.col[sCol]) == 1): #if we are moving the only queen it the column, add the column to the set of empty columns
            self.emptyCol.add(sCol) 
        if (fCol in self.emptyCol): #if the column we are moving to is in the set of empty columns, take it our
            self.emptyCol.remove(fCol)
        self.row[sRow] = fCol #basically the same code as init
        self.col[sCol].remove(sRow)
        self.col[fCol].add(sRow)
        self.leftD[self.realSize - (sRow - sCol)].remove(sCol if (sRow > sCol) else sRow)
        self.leftD[self.realSize - (sRow - fCol)].add(fCol if (sRow > fCol) else sRow)
        self.rightD[2*self.realSize - (sRow + sCol)].remove((self.realSize - sCol) if ((sRow + sCol) >= self.realSize) else sRow)
        self.rightD[2*self.realSize - (sRow + fCol)].add((self.realSize - fCol) if ((sRow + fCol) >= self.realSize) else sRow)
        
    
    #printing
    def printArr(self):
        print(self.row)
        print(self.col)
        print(self.leftD)
        print(self.rightD)

    def getSol(self):
        return list(map(lambda x: x + 1, self.row))

if __name__ == "__main__":
    nqueens()


