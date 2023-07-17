# Bitespeed Backend Task: Identity Reconciliation 

Hi, my name is Gourab Chakraborty. I'm a computer science new grad from IIIT Dharwad. 

## Web Endpoint: 13.50.241.84:3232/identify

You can run this endpoint using postman. I am running this in a EC2 instance. Logs are being logged in a .out file. 
Case considered: script should keep running even when I log out from EC2's SSH.

## Docker endpoint: localhost:3232/identify

just run "docker-compose up" and hit the endpoint in postman

## Note: there is some issue in the expected output in the problem statement:

For the DB:
```
{
	id                   1                   
  phoneNumber          "123456"
  email                "lorraine@hillvalley.edu"
  linkedId             null
  linkPrecedence       "primary"
  createdAt            2023-04-01 00:00:00.374+00              
  updatedAt            2023-04-01 00:00:00.374+00              
  deletedAt            null
},
{
	id                   23                   
  phoneNumber          "123456"
  email                "mcfly@hillvalley.edu"
  linkedId             1
  linkPrecedence       "secondary"
  createdAt            2023-04-20 05:30:00.11+00              
  updatedAt            2023-04-20 05:30:00.11+00              
  deletedAt            null
}
```
It is expected that the response will be:
```
	{
		"contact":{
			"primaryContatctId": 1,
			"emails": ["lorraine@hillvalley.edu","mcfly@hillvalley.edu"],
			"phoneNumbers": ["123456"],
			"secondaryContactIds": [23]   // TO BE NOTED
		}
	}
```
That is it is displaying it's own (the duplicate's) ID in the secondaryContactsIds as well.

But in the last example,
```
{
	id                   11                   
  phoneNumber          "919191"
  email                "george@hillvalley.edu"
  linkedId             null
  linkPrecedence       "primary"
  createdAt            2023-04-11 00:00:00.374+00              
  updatedAt            2023-04-11 00:00:00.374+00              
  deletedAt            null
},
{
	id                   27                   
  phoneNumber          "717171"
  email                "biffsucks@hillvalley.edu"
  linkedId             11
  linkPrecedence       "secondary"
  createdAt            2023-04-21 05:30:00.11+00              
  updatedAt            2023-04-28 06:40:00.23+00              
  deletedAt            null
}
```
It is expected that the response will be:
```
	{
		"contact":{
			"primaryContatctId": 11,
			"emails": ["george@hillvalley.edu","biffsucks@hillvalley.edu"],
			"phoneNumbers": ["919191","717171"],
			"secondaryContactIds": [27]   // TO BE NOTED
		}
	}
```
That is, it's not displaying the new entry's ID in the secondaryContactIDs list. It's showing all the secondaryContactIds other than it's own.

For the solution, I have implemented the second logic (don't show your own contact ID in the secondary contact ID) but in my opinion, we should add our own contact ID too if we are duplicate. It makes more sense (the first example's output). Yet I have implemented the second logic to show that we can implement the logic. Commenting out one additional codeline would return output following the first logic (native). 

## Solutionizing

Since it was specifically asked to update the database with the new states, I have done so. So the database is scanned and updated for every new POST calls.

Downside: Multiple Read operations are done on the database and a few write operations.

If it wasn't mention to update the database state after every entry (via the example), I would have changed the database schema and used a Graph problem algorithm called [Disjoint Set Union](https://cp-algorithms.com/data_structures/disjoint_set_union.html) to find the common roots and the root nodes would have been my primary Ids and the leaf nodes of these rood nodes would be my secondary IDs.
So on every POST API call, I would initally read the entire DB **only once** and write onto the DB if and only when needed. The time taken to find out the rood node and make update (if necessary) and return response (aka response time) could be further reduced by implementing Path Compression optimisation technique. The amortized time complexity is O(a(n)) and the worst case time complexity is O(log(n)) for a chain length of N, number of entries.

## Screenshots:

![Docker compose](https://github.com/gourab337/bitespeed-assignment/blob/main/Screenshot%202023-07-18%20at%202.04.38%20AM.png)

![Postman](https://github.com/gourab337/bitespeed-assignment/blob/main/Screenshot%202023-07-18%20at%202.04.49%20AM.png)
