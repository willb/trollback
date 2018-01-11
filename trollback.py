#!/usr/bin/env python

# requires py-trello 0.10.0
# author: William Benton (self@willbenton.com)
# public domain

from trello import TrelloClient
from os import getenv
from sys import argv, exit
from time import sleep
from collections import namedtuple


if len(argv) != 3:
    print("usage: %s BOARD_NAME SINCE" % argv[0])
    exit(1)
else:
    board_name = argv[1]
    since = argv[2]

client = TrelloClient(
    api_key=getenv("TRELLO_API_KEY"), 
    api_secret=getenv("TRELLO_API_SECRET"),
    token=getenv("TRELLO_TOKEN")
)

boards = [board for board in client.list_boards() if board.name == board_name]

membercache = {}

for board in boards:
    cards = board.get_cards()
    for card in cards:
        # If you need to capture cards that don't have removeMemberFromCard actions,
        # collect the following actions as well:
        #    card.fetch_actions(action_filter='addMemberToCard', since="1990-01-01T00:00:00.00Z")
        m_actions = card.fetch_actions(action_filter='removeMemberFromCard', since=since) 
        
        # This and subsequent sleeps are designed to ensure that we never exceed 
        # Trello's rate limits (100 requests/10 seconds).  The client library makes
        # several API calls within some methods.
        sleep(0.1)
        for action in m_actions:
            
            m_id = action["member"]["id"]
            
            if m_id in membercache:
                member = membercache[m_id]
            else:
                # Construct a member object from the fields of the member dictionary
                m = action["member"]
                member = namedtuple("Member", " ".join(m.keys()))(**m)
            
                
                sleep(0.1)
                membercache[m_id] = member

            card_members = card.idMembers
            print(card, member, card_members)
            try:
                if member.id not in card_members:
                    card.add_member(member)
                    sleep(0.1)
            except Exception as e:    
                print(e)    
