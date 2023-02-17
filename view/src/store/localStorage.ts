type LocalStorageKey = string;

export const saveToLocalStorage = (key: LocalStorageKey, data: any) => {
    try {
        const serializedData = JSON.stringify(data);
        localStorage.setItem(key, serializedData);
    } catch (err) {
        console.error(`Error saving to local storage: ${err}`);
    }
};

export const getFromLocalStorage = <T>(
    key: LocalStorageKey,
    defaultValue: T
): T => {
    try {
        const serializedData = localStorage.getItem(key);
        if (serializedData === null) {
            return defaultValue;
        } else {
            return JSON.parse(serializedData) as T;
        }
    } catch (err) {
        console.error(`Error getting from local storage: ${err}`);
        return defaultValue;
    }
};

export const removeFromLocalStorage = (key: LocalStorageKey) => {
    try {
        localStorage.removeItem(key);
    } catch (err) {
        console.error(`Error removing from local storage: ${err}`);
    }
};
