import { configureStore } from "@reduxjs/toolkit";
import { getFromLocalStorage, saveToLocalStorage } from "./localStorage";
import { useDispatch, useSelector, TypedUseSelectorHook } from "react-redux";
import rootReducer from "./rootReducer";
import { RootState } from "./rootReducer";

const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
  preloadedState: getFromLocalStorage("state", {
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
  }),
});

store.subscribe(() => {
  saveToLocalStorage("state", store.getState());
});

export default store;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

export * from "./localStorage";
export * from "./rootReducer";
export type { RootState };
