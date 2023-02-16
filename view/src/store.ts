import { configureStore, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { TypedUseSelectorHook, useDispatch, useSelector } from "react-redux";

// load initial from local storage
const initialState = JSON.parse(localStorage.getItem("state") || "{}");

// create slice
const slice = createSlice({
  name: "app",
  initialState,
  reducers: {
    setCredential: (
      state,
      action: PayloadAction<{ username: string; password: string }>
    ) => {
      state.crendential = action.payload;
    },
    clearCredential: (state) => {
      state.crendential = null;
    },
    configureGrade: (
      state,
      action: PayloadAction<{ weighted: boolean; normalize: boolean }>
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
  localStorage.setItem("state", JSON.stringify(store.getState()));
});

export const {
  setCredential,
  clearCredential,
  configureGrade,
  setCurrentCourse,
} = slice.actions;

export default store;
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
