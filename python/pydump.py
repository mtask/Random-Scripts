#!/usr/bin/python

import argparse, sys, time
from scapy.all import *

"""
Author: mtask@github.com
Program: pydump.py
Description: Simple packet analyzer.

Pydump is made also python3 in mind, but haven't been tested how scapy's python3 version works.
"""

class Pydump(object):

    def __init__(self):
        self.blk = '\033[0m' # Black - Regular
        self.warn = '\033[93m' # yellow
        self.grn = '\033[92m' # Green
        self.fatal = '\033[91m' #red
        self.packetNumber = 0
        
    def arguments(self):
     
        self.parser = argparse.ArgumentParser(description="Packet capturing tool", prog="pydump.py")
        self.parser.add_argument("-i", "--iface", help="Capturing interface")
        self.parser.add_argument("-n", "--num", help="Number of packets to capture")
        self.parser.add_argument("-r", "--read", help="Read .pcap file")
        self.parser.add_argument("-f", "--filter", help="Filter packets. Use quotes(\"\")")
        self.parser.add_argument("-w", "--write", help="Write capture to file")
        self.parser.add_argument("-I", "--inspect", action='store_true', help="Inspect packets")
        
        self.args = self.parser.parse_args()
        if not self.args.iface and not self.args.read:
            self.parser.print_usage()
            sys.exit(self.fatal+"[!] No interface selected"+self.blk)
            
        else:
            return self.args
            
    def output(self, packet):
        """
        Standard sniffing output
        """
        self.packetNumber += 1
        time.sleep(1)
        return str(self.packetNumber) + ": " + packet.summary()

                      
    def sniffer(self,iface, filter_=None, num=None):
        ######################################
        #Sniffing with scapy.                #
        #sniffer() returns captured packets, #           
        #or False if none captured.          #
        ######################################
        
        self.fil = filter_
        self.iface = iface
        self.num = num
        self.statement = self.output

        
        
        ###Check if --num/--filter used and start capturing###   
        
        if self.num:
            try:
                print("Capturing "+ self.num + " packets from " + self.iface)
                if self.fil:
                    self.pckts = sniff(iface=self.iface,filter=self.fil, count=int(num), prn = self.statement)
                    
                else:
                    self.pckts = sniff(iface=self.iface,  count=int(num), prn = self.statement)
                    
            except NameError:
                print(self.fatal+"Check your filtering argument"+self.blk)
                sys.exit(2)
                
            except socket.error as se:
                print(self.fatal+str(se)+": "+self.iface+self.blk)
                sys.exit(2)

                
        elif not self.num:
            try:
               print("Capturing traffic from "+self.iface)
               
               if self.fil:
                   self.pckts = sniff(iface=self.iface, filter=self.fil, prn = self.statement)
               else:
                   self.pckts = sniff(iface=self.iface, prn = self.statement)
            except NameError:
                print(self.fatal+"Check your filtering argument"+self.blk)
                sys.exit(2)
                
            except socket.error as se:
                print(self.fatal+str(se)+": "+self.iface+self.blk)
                sys.exit(2)

                
        if self.pckts:
            return self.pckts
        else:
            return False
                         
    def main(self):
        ###Checking arguments###
    
        self.arg = self.arguments()
        self.iface_ = self.arg.iface
        
        if self.arg.filter:
            self.fil_ = self.arg.filter
        else:
            self.fil_ = None
            
        if self.arg.num:
            self.num_ = self.arg.num
        else:
            self.num_ = None
            
        ###If --read###
        if self.arg.read:
            self.pcapfile = self.arg.read
            try:
                self.rdpkt=rdpcap(self.pcapfile)
                self.rdpkt.nsummary()
            except Exception as e:
                sys.stderr.write(self.fatal+e+self.blk)
                sys.exit(2)
          
        ###Start packet sniffing###
        
        self.cap = self.sniffer(self.iface_, filter_=self.fil_, num=self.num_)
         
        ###Write captured packets to file if --write###
        if self.cap:
            if self.arg.write:
                self.file_ = self.arg.write
                if ".pcap" in self.file_:
                    wrpcap(self.file_, self.cap)
                else:
                    self.file_ = self.file_+".pcap"
                    wrpcap(self.file_,  self.cap)
                   
        ###If inspection mode selected###

            if self.arg.inspect:
                self.inspect = Inspect()
                os.system('clear')
                print(self.grn+"[*] Starting inspection mode.."+self.blk)
                time.sleep(2)
                self.inspect.prompt(self.cap)
                       
        else:  
            sys.exit(self.warn+"[!] No packets were captured"+self.blk)
                

class Inspect(object):

    def __init__(self):
        self.blk = '\033[0m' # Black - Regular
        self.warn = '\033[93m' # yellow
        self.grn = '\033[92m' # Green
        self.fatal = '\033[91m' #red
    
    def get_input(self, prompt):
        #################################################### #
        #Get user input maintaining the python compatibility #
        #with earlier and newer versions.                    #
        ######################################################
        
        if sys.hexversion > 0x03000000:
            return input(prompt)
        else:
            return raw_input(prompt)
    
    def print_usage(self):
        os.system('clear')
        print('--------------------------')
        print(self.grn+'Inspection mode'+self.blk)
        print('--------------------------')
        print(self.grn+'[*] Captured traffic can be viewed with "list" command.')
        print('[*] Give packet number to inspect packet.')
        print('[*] Commands: "help", "list", "exit"')
        print(self.warn+'Press enter to continue'+self.blk)
        self.get_input('...')
        return True
        
    def print_packets(self,packets):
        #Print list of captured packets
        self.packet_number = 1
        for self.packet in packets:
            print(str(self.packet_number)+": " + self.packet.summary())
            self.packet_number += 1
     
    def prompt(self, cap):
        self.cap = cap
        self.option = None
        self.opts = ['list', 'help', 'exit']
        self.print_usage()
        os.system('clear')
        print(self.grn+'[*] Listing packages'+self.blk)
        time.sleep(1)
        self.print_packets(self.cap)
        
        while True:
            try:
                print(self.grn+"- - - - - - - - - - - - - - - - - - - - - ")
                print("Give packet number to inspect or try \"help\":")
                print("- - - - - - - - - - - - - - - - - - - - - "+self.blk)
                    
                ###Get user's option###
                    
                self.choice = self.get_input(">>>")
                try:
                    if self.choice in self.opts:
                        if self.choice.lower() == 'list':
                            self.parser(self.choice, cap=self.cap)
                            continue
                        else:
                            self.parser(self.choice)
                            continue
                      
                    ###Show selected packet###
                         
                    self.choice = int(self.choice) - 1
                    print(self.cap[self.choice].display())
                    self.get_input("Press enter to continue")
                except ValueError:
                    os.system('clear')
                    sys.stderr.write(self.warn+"[!] No such packet or option"+self.blk)
                    time.sleep(2)
                except IndexError:
                    os.system('clear')
                    print(self.warn+"[!] No such packet or option"+self.blk)
                    time.sleep(2)
            except KeyboardInterrupt:
                sys.exit(0)


    def parser(self, option, cap=None):
        #########################
        #Parse option           #
        #########################
        
        self.opt = option
        self.options = {'help': 'List options','list': 'View list of captured packages','exit': 'Exit'}
        
        if self.opt.lower() == 'list' and cap:
            self.print_packets(cap)
        elif self.opt.lower() == 'help':
            print("---Options---")
            for self.opt in self.options:
                print(self.opt + ": " + self.options[self.opt])
            self.get_input("Press enter to continue")
        elif self.opt.lower() == "exit":
            sys.exit()

if __name__ == "__main__":
    pd = Pydump()
    pd.main()