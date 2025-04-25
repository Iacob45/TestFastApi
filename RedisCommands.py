import redis

pool=redis.ConnectionPool(host="127.0.0.1",port=int(6379),db=int(0),password="parola divina23^&")
r = redis.Redis(connection_pool=pool)

#COOL STUFF
print("COOL STUFF")
print(r.keys(),"\n\n") #Return all the keys in the DB

#STRINGS
print("STRINGS")
print(r.set("name","Alun2", xx= True)) #set one string value to a key : SET key value [NX | XX] [GET] [EX seconds | PX milliseconds | EXAT unix-time-seconds | PXAT unix-time-milliseconds | KEEPTTL]
print(r.mset({"Germany": "Berlin", "France": "Paris"})) #set multiple string key pairs
print(r.get("name")) #return one string
print(r.exists("name")) #check if this key exists
print(r.mget("name","Germany", "France")) #return multiple strings
print(r.strlen("name")) #length of string
print(r.substr("name", 3, -1)) #return substring
print(r.incr("rating")) #increment an integer value
print(r.decr("rating")) #decrease an integer value
print(r.delete("name")) #delete key
print(r.incrby("rating",5),"\n\n") #increment with 5

#SETS
print("SETS")
print(r.sadd("set1", "apple", "tomato", "cucumber")) #create set
print(r.srem("set1", "cucumber")) #remove one member
print(r.scard("set1")) #number of members in set
print(r.sismember("set1","apple")) #check if a member is part of the set
print(r.smembers("set1"),"\n\n") #return members of set

#LISTS
print("LISTS")
print(r.lpop("list99", 1)) #pop left
print(r.rpop("list99", 1)) #pop right
print(r.lpush("list99", "potato")) #push left
print(r.rpush("list99", "strawberry")) #push right
print(r.llen("list99")) #length of list
print(r.lindex("list99", 0)) #value of index
print(r.lpos("list99", "potato"), "\n\n") #index of value


#HASHES
print("HASHES")
print(r.hgetall("books:2")) #return all information from Hash
print(r.hkeys("books:2")) #return all keys from Hash
print(r.hvals("books:2"),"\n\n") #return all values from Hash


