from hashlib import blake2b
import redis
import settings as _settings
import uuid
import pickle


# Cache implementation using Redis
class Cache(object):
    def __init__(self):
        self._task_q = self._get_entity_name(_settings.TASK_QUEUE_NAME)
        self._task_list = self._get_entity_name(_settings.JOB_ORDERED_LIST)
        self._redis = self._init_redis()

    def _get_entity_name(self, name):
        hash_digest = blake2b(digest_size=20)
        hash_digest.update(name.encode('utf-8'))
        entity_name = "%s:%s" % (name, hash_digest.hexdigest())
        return entity_name

    def _init_redis(self):
        r = redis.Redis(
            host=_settings.HOST,
            port=_settings.PORT,
            db=_settings.DATABASE
        )
        return r

    def put_datablock(self, datablock):
        datahash = blake2b(digest_size=20)
        datahash.update(datablock.encode('utf-8'))
        datablock_id = "%s:%s" % (_settings.DATABLOCK_PREFIX, datahash.hexdigest())

        self._redis.set(datablock_id, datablock)

        return datablock_id

    def get_current_window_size(self, window_key):
        n_objs = self._redis.llen(window_key)
        return n_objs

    def assign_datablock_to_window(self, window_key, datablock_id):
        n = self._redis.lpush(window_key, datablock_id)
        return n

    # Inserts entries to task-list and task-queue
    def create_task(self, *datablock_ids):
        task_uuid = "%s:%s" % (_settings.TASK_PREFIX, str(uuid.uuid4()))
        self._redis.rpush(self._task_list, task_uuid)
        task_tuple = pickle.dumps((task_uuid, *datablock_ids, "custom"))
        #print(task_uuid, *datablock_ids)
        # CHECK: why directly adding a tuple fails?
        #self._redis.lpush(self._task_q, (task_uuid, *datablock_ids, "custom"))
        self._redis.lpush(self._task_q, task_tuple)

    # Retrieves datablock-ids within a window
    def get_windowed_datablocks(self, window_key):
        datablock_ids = []
        for i in range(0, self._redis.llen(window_key)):
            datablock_ids.append(self._redis.lindex(window_key, i))
        return datablock_ids





