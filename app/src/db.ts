
import { openDB, deleteDB, wrap, unwrap, IDBPDatabase, DBSchema } from 'idb';
import { SessionDetail, UserDetail } from './client';

export function randomString(n: number, charset?: string): string {
    let res = '';
    let chars =
        charset || 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let charLen = chars.length;

    for (var i = 0; i < n; i++) {
        res += chars.charAt(Math.floor(Math.random() * charLen));
    }

    return res;
}

interface DataStoreDB extends DBSchema {
    kvstore: {
        value: {key:string, value:object | string | number};
        key: string;
    };
    app_kvstore: {
        value: {app_id:string, key:string, value:object | string | number};
        key: [string, string];
    };
}

export class DataStore {
    static db: IDBPDatabase<DataStoreDB> | undefined

    static async init() {
        if( !this.db){
            const db = await openDB<DataStoreDB>('highorder-store', 2, {
                upgrade(db) {
                    db.createObjectStore('kvstore', {
                        keyPath: 'key',
                        autoIncrement: false,
                    });
                    db.createObjectStore('app_kvstore', {
                        keyPath: ['app_id', 'key'],
                        autoIncrement: false,
                    });
                },
            });
            this.db = db
        }
    }

    static async get(key: string){
        if(! this.db){
            await this.init()
        }
        const store = this.db?.transaction('kvstore').objectStore('kvstore');
        const value_obj = await store?.get(key)
        if (value_obj !== undefined){
            return value_obj.value
        }
        return undefined
    }

    static async save(value: {key:string, value:object | string | number}){
        const tx = this.db?.transaction('kvstore', 'readwrite');
        const store = tx?.objectStore('kvstore');
        await store?.put(value);
        await tx?.done;
    }

    static async get_app_kv(key: [string, string]){
        if(! this.db){
            await this.init()
        }
        const store = this.db?.transaction('app_kvstore').objectStore('app_kvstore');
        const value_obj = await store?.get(key)
        if (value_obj !== undefined){
            return value_obj.value
        }
        return undefined
    }

    static async save_app_kv(value: {app_id:string, key:string, value:object | string | number}){
        const tx = this.db?.transaction('app_kvstore', 'readwrite');
        const store = tx?.objectStore('app_kvstore');
        await store?.put(value);
        await tx?.done;
    }

    static async delete_app_kv(value: {app_id:string, key:string}){
        const tx = this.db?.transaction('app_kvstore', 'readwrite');
        const store = tx?.objectStore('app_kvstore');
        await store?.delete([value.app_id, value.key]);
        await tx?.done;
    }
}


export class AppDataStore {
    static instances: Record<string, AppDataStore>  = {}

    app_id: string

    static async get_store(app_id: string){
        if(this.instances.hasOwnProperty(app_id)){
            return this.instances[app_id]
        } else {
            const store = new AppDataStore(app_id)
            this.instances[app_id] = store
            await store.genInitValue()
            return store
        }

    }

    async genInitValue() {
        const value = await DataStore.get_app_kv([this.app_id, 'local_uid']) as string
        if( value === undefined){
            const local_uid = randomString(32)
            await DataStore.save_app_kv({
                app_id: this.app_id,
                key:'local_uid',
                value: local_uid
            })
        }

    }

    constructor(app_id: string){
        this.app_id = app_id
    }

    async getLocalUid(): Promise<string | undefined> {
        return await DataStore.get_app_kv([this.app_id,'local_uid']) as string
    }

    async getCustomUid(): Promise<string | undefined> {
        return await DataStore.get_app_kv([this.app_id,'custom_uid']) as string
    }

    async saveCustomUid(custom_uid: string){
        await DataStore.save_app_kv({app_id: this.app_id, key: 'custom_uid', value: custom_uid})
    }

    async saveUser(user: UserDetail){
        await DataStore.save_app_kv({app_id: this.app_id, key: 'user', value: user})
    }

    async getUser(): Promise<UserDetail | undefined> {
        return await DataStore.get_app_kv([this.app_id,'user']) as UserDetail
    }

    async deleteUser() {
        await DataStore.delete_app_kv({app_id: this.app_id, key: 'user'})
    }

    async saveSession(session: SessionDetail){
        await DataStore.save_app_kv({app_id: this.app_id, key: 'session', value: session})
    }

    async getSession(): Promise<SessionDetail | undefined> {
        return await DataStore.get_app_kv([this.app_id, 'session']) as SessionDetail
    }

    async deleteSession() {
        await DataStore.delete_app_kv({app_id: this.app_id, key: 'session'})
    }
}
