#Created by Kin-Ho Lam 9/21/15 for the COF helpdesk.
#This scripts checks mysql db to grab list of unified users.
#Requires Python 2.7 and MySQLdb Python 1.2.5
import MySQLdb, sys, os, getopt, re

#in python I use global arrays, idgaf
users = []; #2D array of users from databases.
db_list  = []; #list of databases taken from the .txt (default db_source.txt)
user_list = []; #list of users from the .txt (default users_source.txt)

def users_groups(): #creates a .csv that lists all users from user_list and lists all tables they appear in
	if(os.path.exists("user_groups.csv")):
		os.remove("user_groups.csv");
	usr_group = open('user_groups.csv', 'w+');
	for item in user_list: #for each user
		usr_group.write(item + ","); #write their name and deliminate by a comma
		for i in xrange(0, len(db_list)):
			if item in users[i]: #if they appear in a database as sorted in the 2D array
				usr_group.write(db_list[i] + ","); #write down the database that they appear in deliminated by a comma
		usr_group.write("\n");

def groups_users(): #creates a .csv that lists all groups from db_list and lists all intersecting users from user_list
	if(os.path.exists("groups_users.csv")):
		os.remove("groups_users.csv");
	group_usr = open('groups_users.csv', 'a+');
	for i in xrange(0,len(db_list)): #for each databases
		temp_array = user_list; #reset and create a temporary array that points to the list of users we want to check
		group_usr.write(db_list[i] + ","); #write each database in the .csv as it appears diliminated by a comma
		temp_array = list(set(temp_array)&(set(users[i]))); #temp array = whatever is common between users in the db
		for item in temp_array:
			group_usr.write(item + ","); #write common users down
		group_usr.write("\n");
	del temp_array[:];

def users_no_group(): #creates a .csv that lists all users from user_list that do not have a group
	temp_array = user_list;
	if(os.path.exists("users_no_group.csv")):
		os.remove("users_no_group.csv");
	no_mem = open('users_no_group.csv', 'w+');
	for x in users:
		temp_array = list(set(temp_array) -  set(x)); #iterate through all database tables removing users from temp_array that are in the database, leaving only users who are not listed
	for item in temp_array:
		no_mem.write(item.replace("\n","").replace("\r","") + "\n");
	del temp_array[:];

def get_source_db(src_db): #takes list of databases to check from .txt file and puts them into db_list array
	if(os.path.exists(src_db)):
		dbsrc = open(src_db, 'r');
	else:
		print "Could not find ", src_db;
		sys.exit(2);
	for line in dbsrc:
		db_list.append(line.replace("\n","").replace("\r","").lower());

def get_source_users(src_usr): #takes list of names to check from .txt file and puts them into user_list array
	if(os.path.exists(src_usr)):
		usrsrc = open(src_usr, 'r');
	else:
		print "Could not find ", src_usr;
		sys.exit(2);
	for line in usrsrc:
		user_list.append(line.replace("\n","").replace("\r","").lower());

def get_db_users(hos, usr, pwd, database): #connects to databases and tries to grab list of users. 
	try:
		db = MySQLdb.connect(host= hos, user= usr, passwd= pwd,db=database);
	except:
		print "Error connecting to remote host db"
		sys.exit(2)
	cur = db.cursor();
	try:
		cur.execute("SELECT name FROM default_users") #default tries to look for default_users table
	except: 
		print "Table Error, no default_users table for " + database + ". Closing." #if the default_user table is not found then script exits
		sys.exit(2);
	for row in cur.fetchall():
		users[len(users)-1].append(row[0].replace("\n","").replace("\r","").lower()); #creates 2d array (list of lists) for each table

def print_all(): #prints db name and listed users
	for i in xrange(0,len(db_list)):
		print "\n"+db_list[i]
		for item in users[i]:
			print item;
		
def main(argv): #main
	host = 'server here';#default options
	user = 'sql login here';
	pwd = 'sql pass here';
	source_db = 'db_source.txt';
	source_users = 'users_source.txt';

	show_all_users = False;
	
	try: #start of command line argument check type --help for options
		opts, args = getopt.getopt(argv,"h:u:p:s:d:v");
	except getopt.GetoptError:
		print "\nDefault settings will be used for all unspecified inputs.\nInputs:\n\t-h <sql host>\n\t-u <sql username> \n\t-p <sql password>\n\t-s <list of users.txt> \n\t-d <list of databases to check.txt> \n\t-v Displays database names and their users."
		sys.exit(2);
	for opt, arg in opts:
		if opt in ("-h"):
			host = arg
		elif opt in ("-u"):
			user = arg
		elif opt in ("-p"):
			pwd = arg
		elif opt in ("-s"):
			source_users = arg
		elif opt in ("-d"):
			source_db = arg
		elif opt in ("-v"):
			show_all_users = True;

	print "\n\t\t     Host: ", host; #prints what settings are being used
	print "\t\t Username: ",user;
	print "\tList of databases: ",source_db;
	print "\t    List of users: ",source_users, "\n";
	get_source_db(source_db);
	get_source_users(source_users);
	for item in db_list:
		users.append([]); #creates pointer for list of lists (2d array)
		get_db_users(host, user, pwd, item.replace("\n","").replace("\r","")); #fills 2D array
	groups_users(); # calls to create .csv files 
	users_groups(); 
	users_no_group();
	if (show_all_users):
		print_all();
	del users[:]; #delete arrays just incase
	del db_list[:];
	del user_list[:];
if __name__ == "__main__": #call to main to check for command line prompts
   main(sys.argv[1:])