import { openDB } from 'idb'

const DB_NAME = 'highorder-webclient'
const DB_VERSION = 1

async function getDB() {
  return await openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains('app')) {
        db.createObjectStore('app')
      }
      if (!db.objectStoreNames.contains('global')) {
        db.createObjectStore('global')
      }
    }
  })
}

export const DataStore = {
  async get(key) {
    const db = await getDB()
    return await db.get('global', key)
  },
  async save({ key, value }) {
    const db = await getDB()
    await db.put('global', value, key)
  },
  async get_app_kv([app_id, key]) {
    const db = await getDB()
    return await db.get('app', `${app_id}:${key}`)
  },
  async save_app_kv({ app_id, key, value }) {
    const db = await getDB()
    await db.put('app', value, `${app_id}:${key}`)
  }
}

export const AppDataStore = {
  async getUser(app_id) {
    const db = await getDB()
    return await db.get('app', `${app_id}:user`)
  },
  async saveUser(app_id, user) {
    const db = await getDB()
    await db.put('app', user, `${app_id}:user`)
  },
  async deleteUser(app_id) {
    const db = await getDB()
    await db.delete('app', `${app_id}:user`)
  },
  async getSession(app_id) {
    const db = await getDB()
    return await db.get('app', `${app_id}:session`)
  },
  async saveSession(app_id, session) {
    const db = await getDB()
    await db.put('app', session, `${app_id}:session`)
  },
  async deleteSession(app_id) {
    const db = await getDB()
    await db.delete('app', `${app_id}:session`)
  },
  async getLocalUid(app_id) {
    const db = await getDB()
    return await db.get('app', `${app_id}:local_uid`)
  },
  async ensureLocalUid(app_id, randomString) {
    const key = `${app_id}:local_uid`
    const db = await getDB()
    const existing = await db.get('app', key)
    if (existing) return existing
    const uid = randomString(16)
    await db.put('app', uid, key)
    return uid
  }
}
