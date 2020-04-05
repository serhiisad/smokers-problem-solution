
# Cigarette Smokers Problem Solution
#
# Three Smokers and one Agent, the Agent pulls out one of the three ingredients of a cigarette (Tobacco, Paper or Match)
# while each of the smokers hold only one ingredient different than each other
# 1st Smoker has infinite amount of Tobacco
# 2nd Smoker has inf a-t of Papers
# 3rd Smoker has inf a-t of Matches
# Each time any smoker is done smoking he needs ingredients for a new cigarette
# An agent has to fulfill everyone

import threading
import random
import time

def generateRandomItems():
    item1 = random.randint(1, 100)
    item2 = random.randint(1, 100)
    item1 %= 3
    item2 %= 3
    if (item1 == item2):
        item2 += 1
        item2 %= 3
    itemList = [item1, item2]
    return itemList


class Smoker:
    def __init__(self, rounds):
        self.condMutex = threading.Condition()
        self.agentSleep = threading.Semaphore(0)
        self.rounds = rounds # number of smokings
        self.ingredients = ['TOBACCO', 'PAPER', 'MATCHES']

        # No item is available on table initially
        self.availableItems = [False, False, False]
        self.smokerThreads = []
        self.terminate = False

        #  3 smokers threads.
        self.smokerThreads.append(threading.Thread(target=self.smokerRoutine, \
                                                   name='Smoker_WithTobacco', args=(1, 2)))
        self.smokerThreads.append(threading.Thread(target=self.smokerRoutine, \
                                                   name='Smoker_WithPaper', args=(0, 2)))
        self.smokerThreads.append(threading.Thread(target=self.smokerRoutine, \
                                                   name='Smoker_WithMatches', args=(0, 1)))
        for smokers in self.smokerThreads:
            smokers.start()
        # Create agent thread. (agent distributes ingredients to smokers)
        self.agentThread = threading.Thread(target=self.agentRoutine)
        self.agentThread.start()

    def agentRoutine(self):
        for i in range(self.rounds):
            # Generate two random items.
            randomItems = generateRandomItems()
            self.condMutex.acquire()
            print('agent produced: {0} and {1}'. \
                  format(self.ingredients[randomItems[0]], \
                         self.ingredients[randomItems[1]]))
            # Make items available on table.
            self.availableItems[randomItems[0]] = True
            self.availableItems[randomItems[1]] = True
            # Announce to all smokers that items are made available on table.
            self.condMutex.notify_all()
            self.condMutex.release()
            # Go to sleep till the selected smoker is done with smoking.
            self.agentSleep.acquire()

    def smokerRoutine(self, neededItem1, neededItem2):
        myName = threading.currentThread().getName()
        while (True):
            self.condMutex.acquire()
            # Block till the needed items are on table.
            while (False == self.availableItems[neededItem1] or
                   False == self.availableItems[neededItem2]):
                self.condMutex.wait()
            self.condMutex.release()
            # Check if it was a terminate signal.
            if (True == self.terminate):
                break
            # Pickup the items from the table.
            self.availableItems[neededItem1] = False
            self.availableItems[neededItem2] = False
            # All ingredients are there,  starting smoking.
            print('{0} started smoking.'.format(myName))
            self.startSmoking()
            print('{0} ended smoking!'.format(myName))
            # Smoking is done, wakeup the sleeping agent.
            self.agentSleep.release()

    def startSmoking(self):
        randomTime = random.randint(1, 100)
        randomTime %= 5
        time.sleep(randomTime + 1)

    def waitForCompletion(self):
        # Wait for agent thread to end.
        self.agentThread.join()
        # Send terminate signal to smoker threads.
        self.condMutex.acquire()
        self.terminate = True
        self.availableItems = [True, True, True]
        self.condMutex.notify_all()
        self.condMutex.release()


if __name__ == "__main__":
    obj = Smoker(15)
    obj.waitForCompletion()