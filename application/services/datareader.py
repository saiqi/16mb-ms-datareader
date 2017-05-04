import pymonetdb
from nameko.rpc import rpc

from application.dependencies.monetdb import MonetDbConnection


class DatareaderService(object):
    name = 'datareader'

    connection = MonetDbConnection()

    @rpc
    def select(self, query, parameters=None):
        cursor = self.connection.cursor()

        try:
            if parameters is None:
                cursor.execute(query)
            else:
                cursor.execute(query, parameters)
        except pymonetdb.exceptions.Error:
            self.connection.rollback()
            raise

        meta = [r[0] for r in cursor.description]

        raw_data = cursor.fetchall()

        results = list()

        for r in raw_data:
            results.append(dict(zip(meta, r)))

        cursor.close()

        return results
