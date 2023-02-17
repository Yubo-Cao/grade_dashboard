import {
  configureStore,
  createSelector,
  createSlice,
  PayloadAction,
} from "@reduxjs/toolkit";
import { TypedUseSelectorHook, useDispatch, useSelector } from "react-redux";

// load initial from local storage
type StateType = {
  credential: {
    username?: string;
    password?: string;
  };
  config: {
    weighted: boolean;
    normalize: boolean;
    notify: boolean;
  };
  currentCourse: string;
};

const initialState: StateType = {
  credential: {
    username: "",
    password: "",
  },
  config: {
    weighted: false,
    normalize: false,
    notify: false,
  },
  currentCourse: "",
};

// create slice
const slice = createSlice({
  name: "app",
  initialState,
  reducers: {
    setCredential: (
      state,
      action: PayloadAction<StateType['credential']>
    ) => {
      state.credential = action.payload;
    },
    clearCredential: (state) => {
      state.credential = {};
    },
    configureGrade: (
      state,
      action: PayloadAction<StateType['config']>
    ) => {
      state.config = action.payload;
    },
    setCurrentCourse: (state, action: PayloadAction<string>) => {
      state.currentCourse = action.payload;
    },
  },
});

// create store
const store = configureStore({
  reducer: slice.reducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

// save to local storage
store.subscribe(() => {
  if (window !== undefined)
    localStorage.setItem("state", JSON.stringify(store.getState()));
});

export const {
  setCredential,
  clearCredential,
  configureGrade,
  setCurrentCourse,
} = slice.actions;

export const selectCredential = createSelector(
  (state: RootState) => state.credential,
  (credential) => credential
);
export const selectConfig = createSelector(
  (state: RootState) => state.config,
  (config) => config
);

export default store;
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
