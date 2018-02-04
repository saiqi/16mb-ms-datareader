from nameko.rpc import rpc
import bson.json_util

from application.dependencies.monetdb import MonetDbConnection


class DatareaderService(object):
    name = 'datareader'

    connection = MonetDbConnection()

    @rpc
    def select(self, query, parameters=None, fetchone=False, limit=50):
        cursor = self.connection.cursor()

        if limit > 0:
            performed_query = '{} LIMIT {}'.format(query, limit)
        else:
            performed_query = query

        if parameters is None:
            cursor.execute(performed_query)
        else:
            cursor.execute(performed_query, parameters)

        results = None
        if cursor.description:
            meta = [r[0] for r in cursor.description]

            if fetchone:
                raw_data = cursor.fetchone()
                results = dict(zip(meta, raw_data))
            else:
                raw_data = cursor.fetchall()

                results = list()

                for r in raw_data:
                    results.append(dict(zip(meta, r)))

        cursor.close()

        return bson.json_util.dumps(results)
