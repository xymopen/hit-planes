from datetime import datetime, timedelta

def every( context = None, *args, **kwargs ):
    delta = timedelta( *args, **kwargs )
    
    if context is None:
        context = lambda x: None

    def every_decorator( fn ):
        context.lastdt = datetime.now()

        def new( *args, **kwargs ):
            nowdt = datetime.now()

            if ( nowdt - context.lastdt > delta ):
                context.lastdt = nowdt
                return fn( *args, **kwargs )
				
        return new
    return every_decorator

def timestamp( dt ):
	return int( ( dt - datetime( 1970, 1, 1 ) ).total_seconds() * 1000 )

def constrain( value, lower, upper ):
	return min( ( max( ( value, lower ) ), upper ) )

def between( value, lower, upper ):
	return lower < value and value < upper
	