# DURL=`psq -U zlochms -d cloudstats -c "SELECT url FROM stats WHERE domain='Cross_domain' AND title LIKE '%Museum%'" -t -A`
# curl -L "$DURL/datapackage.json" -o datapackage.json

# -----------------

# preparation
#
# + import tsv file into database
# + obtain download urls from datahub.io (extends database table)

import re
import os
import argparse
import psycopg2

def ensure_db_schema_complete( r, cur ):
    ```ensure_db_schema_complete```

    cur.execute( "SELECT column_name FROM information_schema.columns WHERE table_name = 'stats';" )

    if not r['format']:
        # TODO create error message and exit
        return False;

    attr = re.sub( r'[+/]', '_', r['format'] )
    if attr not in cur.fetchall():
        cur.execute( "ALTER TABLE stats ADD COLUMN '"+ attr +"' varchar;" )

    return attr

def save_value( cur, datahub_url, attribute, value, check=True ):
    ```save_value```

    if check and not value:
        # TODO create warning message
        print 'no value for attribute '+ attribute +'. could not save'
    else:
        cur.execute( 'UPDATE stats SET '+ attribute +'="'+ value +'" WHERE url = "'+ datahub_url +'";' )

def parse_resource_urls( datahub_url, dry_run=False ):
    ```parse_resource_urls```

    os.popen( 'curl -L "'+ datahub_url +'/datapackage.json" -o datapackage.json ' )
    # TODO ensure the process succeeds

    file = './datapackage.json'
    with open( file, 'r' ):
        try:
            dp = json.load( file )

            if not dp['resources']:
                # TODO create error message and exit
                return None

            for r in dp['resources']:
                attr = ensure_db_schema_complete( r, cur )

                if not attr:
                    continue

                save_value( cur, datahub_url, dp, attr, r['url'], False )

            save_value( cur, datahub_url, 'name', dp['name'] if 'name' in dp else None )
            save_value( cur, datahub_url, 'keywords', dp['keywords'] if 'keywords' in dp else None )
            # save whole datapackage.json in column
            save_value( cur, datahub_url, 'datapackage_content', str( json.dumps( dp ) ), False )

        except:
            # TODO create error message and exit
            return None

    return 

# -----------------

# real job
def download_dataset( ds_url, ds_format, dry_run=False ): 
    ```download_dataset```


    return filepath_str

def build_graph_prepare( file, dry_run=False ):
    ```build_graph_prepare```
    
def build_graph( file, stats={}, dry_run=False ):
    ```build_graph```

def save_stats( stats, sid ):
    ```save_stats```

#dry_run = True
#
#cur.execute( 'SELECT id,url,format FROM stats' + ';' if not dry_run else ' WHERE domain="Cross_domain" AND title LIKE "%Museum%";' )
#datasets = cur.fetchall()
#
#for ds in datasets:
#    
    #file = None
#    
    #try:
        #file = download_dataset( ds[1],ds[2], dry_run )
    #except:
        ## save error in error-column
        #continue
#    
    #stats = {}
#    
    #build_graph_prepare( file, dry_run )
    #build_graph( file, stats, dry_run )
    #save_stats( stats, ds[0] )

# -----------------

if __name__ == '__main__':

    parser = argparse.ArgumentParser( description = 'lodcc' )
    parser.add_argument( '--parse-resource-urls', '-u', action = "store", type = bool, help = '', default = False )
    parser.add_argument( '--dry-run', '-d', action = "store", type = bool, help = '', default = False )

    # read all properties in file into args-dict
    if os.path.isfile( 'db.properties' ):
        with open( 'db.properties', 'rt' ) as f:
            args = dict( ( key.replace( '.', '-' ), value ) for key, value in ( re.split( "=", option ) for option in ( line.strip() for line in f ) ) )
    else:
        parser.add_argument( '--db-host', '-H', action = "store", type = str, help = '', default = "localhost" )
        parser.add_argument( '--db-user', '-U', action = "store", type = str, help = '', default = "zlochms" )
        parser.add_argument( '--db-password', '-P', action = "store", type = str, help = '', default = "zlochms" )
        parser.add_argument( '--db-dbname', '-S', action = "store", type = str, help = '', default = "zlochms" )

    argsps = parser.parse_args()

    for arg in ['log_level', 'dry_run', 'db-host', 'db-user', 'db-password', 'db-dbname']:
        if not arg in args:
            args[arg] = getattr( argsps, arg )

    # connect to an existing database
    conn = psycopg2.connect( host=args['db-host'], dbname=args['db-dbname'], user=args['db-user'], password=args['db-password'] )
    cur = conn.cursor()

    try:
        cur.execute( "SELECT 1;" )
        result = cur.fetchall()
    except:
        print "Database not ready for query execution. "+ sys.exc_info()[0]
        raise 

    # option 1
    if "parse_resource_urls" in argsps:
        if "dry_run" in args:
            print "Running in dry-run mode"
            print "Using example dataset 'Museums in Italy'"
    
            parse_resource_urls( 'https://old.datahub.io/dataset/museums-in-italy', True )
        else:
            print "not yet implemented. terminating"

    # close communication with the database
    cur.close()
    conn.close()

# -----------------
#
# notes
# - add error-column to table and set it
