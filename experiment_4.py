"""
The task is to simulate an M/M/k system with a single queue.
Complete the skeleton code and produce results for three experiments.
The study is mainly to show various results of a queue against its ro parameter.
ro is defined as the ratio of arrival rate vs service rate.
For the sake of comparison, while plotting results from simulation, also produce the analytical results.
"""

import heapq
import random
import matplotlib.pyplot as plt


# Parameters
class Params:
    def __init__(self, lambd, mu, k):
        self.lambd = lambd  # interarrival rate
        self.mu = mu  # service rate
        self.k = k


    # Note lambd and mu are not mean value, they are rates i.e. (1/mean)

# Write more functions if required


# States and statistical counters
class States:
    def __init__(self):
        # States
        self.queues = []
        self.servers = []
        self.util = 0.0
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0
        self.num_in_q = 0
        self.delay = 0.0
        self.time_of_last_event = 0.0
        self.total_time_served = 0.0
        self.area_num_in_queue = 0.0
        self.no_of_q_avilable = 0

    def update(self, sim, event):
        self.time_since_last_event = sim.simclock - self.time_of_last_event
        self.time_of_last_event = sim.simclock
        self.total_time_served += (((sim.params.k - self.no_of_q_avilable) / sim.params.k) * self.time_since_last_event)

        #self.total_time_served += (self.server_status * self.time_since_last_event)
        i=0
        total_customers = 0
        while i < sim.params.k:
            total_customers += len(self.queues[i])
            i+=1
        self.area_num_in_queue += self.time_since_last_event * (total_customers/sim.params.k)

    def finish(self, sim):
        self.avgQdelay = self.delay / self.served
        self.avgQlength = self.area_num_in_queue / sim.simclock
        self.util = self.total_time_served / sim.simclock



    def finish1(self, sim):
        if self.served >= 1:
            self.avgQdelay = self.delay / self.served
        else:
            self.avgQdelay = 0.0

        mean_time = (self.total_time_served + self.delay) / self.served
        #self.avgQlength = mean_time / sim.simclock * self.served
        self.avgQlength = self.area_num_in_queue / sim.simclock
        # if self.total_time_served >= sim.simclock:
        #    self.util=1
        # else :
        #    self.util = self.total_time_served / sim.simclock
        #   print ('Total time served %f' %self.total_time_served)
        self.util = self.total_time_served / sim.simclock


    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        print('MMk Results: lambda = %lf, mu = %lf, k = %d' % (sim.params.lambd, sim.params.mu, sim.params.k))
        print('MMk Total customer served: %d' % (self.served))
        print('MMk Average queue length: %lf' % (self.avgQlength))
        print('MMk Average customer delay in queue: %lf' % (self.avgQdelay))
        print('MMk Time-average server utility: %lf' % (self.util))

    def getResults(self, sim):
        return (self.avgQlength, self.avgQdelay, self.util)

# Write more functions if required


class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None

    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')

    def __repr__(self):
        return self.eventType


class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim

    def process(self, sim):
        Time = sim.simclock + random.expovariate(sim.params.lambd)
        sim.scheduleEvent(ArrivalEvent(Time, sim))


class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        # Complete this function
        None


class ArrivalEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim

    def process(self, sim):
        sim.scheduleEvent(ArrivalEvent((sim.simclock + random.expovariate(sim.params.lambd)) , sim))
        is_any_server_idle = 1
        pos = 0

        while pos < sim.params.k:
            if sim.states.servers[pos] == 0.0:
                is_any_server_idle = 1
                break
            else:
                pos += 1
                is_any_server_idle = 0


        if is_any_server_idle == 1 :
            sim.states.served += 1
            #print('server %i is idle' % pos)
            sim.states.no_of_q_avilable = sim.states.no_of_q_avilable -1
            departure_time = sim.simclock + random.expovariate(sim.params.mu)
            sim.states.servers[pos] = float(departure_time)
            print('making %i server busy' % pos)
            #print(type(sim.states.servers[pos]))
            delay_1 = 0.0
            sim.states.delay += delay_1
            sim.scheduleEvent(DepartureEvent(departure_time, sim))
        else:
            shortest_len_of_q = 1000
            l=0
            queue_no = 0
            while l < sim.params.k :
                length = int(len(sim.states.queues[l]))
                if length < shortest_len_of_q :
                    shortest_len_of_q = len(sim.states.queues[l])
                    queue_no = l
                l += 1
            print('Inserting in queue %i'%queue_no)
            sim.states.num_in_q += 1
            sim.states.queues[queue_no].append(sim.simclock)


class DepartureEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'DEPARTURE'
        self.sim = sim

    def process(self, sim):
        server_number=100
        i = 0
        while i < sim.params.k:
            if sim.states.servers[i] == sim.simclock:
                server_number = i
                print('departing from server %i  ' % i)
                break
            else:
                i+=1

        if server_number != 100:
            if len(sim.states.queues[server_number]) > 0 :
                print('departing from server %i  ' % i)
                sim.states.served = sim.states.served + 1
                time = sim.states.queues[server_number].pop(0)
                sim.states.num_in_q = sim.states.num_in_q - 1
                sim.states.delay = sim.states.delay + (sim.simclock - time)
                depatrure_time = sim.simclock + random.expovariate(sim.params.mu)
                sim.states.servers[server_number] = depatrure_time
                sim.scheduleEvent(DepartureEvent(depatrure_time, sim))
                      ######### checking queue length ###############
                LF = 0
                LR = 0
                diffrence1 = 0
                diffrence2 =0
                if (server_number - 1) >= 0 :
                    LF = len(sim.states.queues[server_number - 1])
                    diffrence1 = LF - sim.states.servers[server_number]
                if (server_number + 1) < sim.params.k :
                    LR = len(sim.states.queues[server_number + 1])
                    diffrence2 = LR - sim.states.servers[server_number]

                if diffrence1 >= 2 or diffrence2 >= 2:
                    while diffrence1 > 1 or diffrence2 > 1:
                        if diffrence1 > 1 :
                            time1 = sim.states.queues[server_number-1].pop(len((sim.states.queues[server_number-1])-1))
                            sim.states.queues[server_number].append(time1)
                        if diffrence2 > 1:
                            time2 = sim.states.queues[server_number + 1].pop(len((sim.states.queues[server_number+1]) - 1))
                            sim.states.queues[server_number].append(time2)
                        if (server_number - 1) >= 0:
                            LF = len(sim.states.queues[server_number - 1])
                            diffrence1 = LF - sim.states.servers[server_number]
                        if (server_number + 1) < sim.params.k:
                            LR = len(sim.states.queues[server_number + 1])
                            diffrence2 = LR - sim.states.servers[server_number]
            else :
                LF = 0
                LR = 0
                diffrence1 = 0
                diffrence2 = 0
                if (server_number - 1) >= 0:
                    LF = len(sim.states.queues[server_number - 1])
                    diffrence1 = LF - sim.states.servers[server_number]
                if (server_number + 1) < sim.params.k:
                    LR = len(sim.states.queues[server_number + 1])
                    diffrence2 = LR - sim.states.servers[server_number]

                if diffrence1 >= 2 or diffrence2 >= 2:
                    while diffrence1 > 1 or diffrence2 > 1:
                        if diffrence1 > 1:
                            time1 = sim.states.queues[server_number - 1].pop(
                                len((sim.states.queues[server_number - 1]) - 1))
                            sim.states.queues[server_number].append(time1)
                        if diffrence2 > 1:
                            time2 = sim.states.queues[server_number + 1].pop(
                                len((sim.states.queues[server_number + 1]) - 1))
                            sim.states.queues[server_number].append(time2)
                        if (server_number - 1) >= 0:
                            LF = len(sim.states.queues[server_number - 1])
                            diffrence1 = LF - sim.states.servers[server_number]
                        if (server_number + 1) < sim.params.k:
                            LR = len(sim.states.queues[server_number + 1])
                            diffrence2 = LR - sim.states.servers[server_number]

                if len(sim.states.queues[server_number]) > 0:
                    sim.states.served = sim.states.served + 1
                    time = sim.states.queues[server_number].pop(0)
                    sim.states.num_in_q = sim.states.num_in_q - 1
                    sim.states.delay = sim.states.delay + (sim.simclock - time)
                    depatrure_time = sim.simclock + random.expovariate(sim.params.mu)
                    sim.states.servers[server_number] = depatrure_time
                    sim.scheduleEvent(DepartureEvent(depatrure_time, sim))

                else:
                    sim.states.servers[server_number]=0.0
                    sim.states.no_of_q_avilable = sim.states.no_of_q_avilable + 1





class Simulator:
    def __init__(self, seed):
        self.eventQ = []
        self.simclock = 0
        self.seed = seed
        self.params = None
        self.states = None

    def initialize(self):
        self.simclock = 0
        self.scheduleEvent(StartEvent(0, self))

    def configure(self, params, states):
        self.params = params
        self.states = states

    def now(self):
        return self.simclock

    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))

    def run(self):
        random.seed(self.seed)
        self.states.no_of_q_avilable = self.params.k
        i = 1
        while i <= self.params.k :
             self.states.queues.append([])
             self.states.servers.append(0.0)
             i += 1

        self.initialize()

        while len(self.eventQ) > 0:
            if self.simclock >= 30000:
                self.scheduleEvent(ExitEvent(self.simclock, self))
            time, event = heapq.heappop(self.eventQ)

            if event.eventType == 'EXIT':
                break

            if self.states != None:
                self.states.update(self, event)

            print(event.eventTime, 'Event', event)
            self.simclock = event.eventTime
            event.process(self)

        self.states.finish(self)

    def printResults(self):
        self.states.printResults(self)

    def getResults(self):
        return self.states.getResults(self)



def experiment4():
    # Similar to experiment2 but for different values of k; 1, 2, 3, 4
    # Generate the same plots
    # Fix lambd = (5.0/60), mu = (8.0/60) and change value of k
    seed = 110
    mu = 8.0 / 60
    lambd = 5.0 / 60
    k = [u for u in range(1, 5)]

    avglength = []
    avgdelay = []
    util = []

    for ks in k:
        sim = Simulator(seed)
        # sim.configure(Params(mu * ro, mu, 3), States())
        sim.configure(Params(lambd, mu, ks), States())
        sim.run()
        sim.printResults()
        length, delay, utl = sim.getResults()
        avglength.append(length)
        avgdelay.append(delay)
        util.append(utl)

    plt.figure(1)
    plt.subplot(311)
    plt.plot(k, avglength)
    plt.xlabel('Server (k)')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(k, avgdelay)
    plt.xlabel('Server(k)')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(k, util)
    plt.xlabel('Server(k)')
    plt.ylabel('Util')

    plt.show()


def main():

    experiment4()



main()