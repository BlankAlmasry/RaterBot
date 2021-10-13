# RaterBot

RaterBot is Discord bot that provides and ranking system for any customized game you have on your server  

# Commands

 There is 3 main commands with many aliases:

##  match

    @RaterBot match @player1 @player2 @etc vs @player3 @player4 @etc
it will ask about the match result, once you provide which team won, will return new rating for each player in that match.
example: 

@Ace. 
`Rank : Platinum I 14 LP
 Rating : 2115`
 @Blank 
`Rank : Challenger 603 LP
 Rating : 3203`
 
##  stats

    @RaterBot stats @Ace
it will return user rating, rank, wins/loses, win ratio and his rank on the server.
example: 

 @Ace 

`Rank: Challenger`
 
`Rating: 3202.99`

 `Win/Loses: 20/10` 

 `Win Ratio: 66.67%` 

`Leaderboard: 1th Over 6 players`

##  leaderboard

    @RaterBot leaderboard
it will paginated ranking of the users based on their rating/rank from top to bottom.
users can paginate the list by simply pressing the already existing emotes of ⬅➡ arrows.
example:
 @RaterBot leaderboard

          #Name       #Rank              #Rating  
     #1   Blank       Challenger         3203   
     #2   player4     Diamond II         2453   
     #3   player1     Diamond IV         2258   
     #4   player2     Diamond IV         2258   
     #5   user1       Platinum I         2124   
     #6   Ace         Platinum I         2115   
     #7   player1     Platinum II        2097   
     #8   Orianna Bot Platinum II        2067   
     #9   lmao        Platinum II        2060   
     #10  player3     Platinum II        2032   
       Page 1 of 2 • Your Rank: 6 •  Ace      
