import random
import csv



stype = "Airline Stocks"

class events:

    def __init__(self, otype, em):
        self.otype = otype
        self.em = em
        self.file = open("TakeStock.csv", "r")
        self.data = list(csv.reader(self.file, delimiter=","))
        #print(self.data)
        #self.file.close()
        #return self.data


    def load_event(self, obj):
        data = obj
        #self.em = []
        row = 2
        i = 0
        while row < len(data):
            if data[row][0] == self.otype:
                self.em.append(data[row][0:17])
                print(self.em[i])
                i = i + 1
            row = row + 1
        self.status = "OK"
        return self.status

    def get_random_event(self):
        rng = len(self.em) - 1
        rnum = random.randint(1, rng - 1)
        row = 0
        val = str(rnum)

        event_desc = " "
        event_amount = 0

        if self.em[0][3] == "Amount":
            val_type = "$"
        else:
            val_type = "#"
        while row < len(self.em):
            if val == self.em[row][1]:
                event_desc = self.em[row][2]
                event_amount = self.em[row][3]
                event_amount = event_amount.replace('$', '')
                event_amount = event_amount.replace(',', '')
                event_amount = int(event_amount)
                self.eamt = event_amount
                self.desc = event_desc
            row = row + 1
        if row:
            self.msg = event_desc + ": " + val_type + str(event_amount)
        else:
            self.msg = "No event found"

        return self.msg