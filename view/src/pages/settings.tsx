import {
  selectConfig,
  selectCredential,
  setConfig,
  setCredential,
  useAppDispatch,
  useAppSelector,
} from "@/store";
import RootLayout from "./layout";

export default function Settings() {
  const textStyle = `block
        w-full
        rounded-md
        border-gray-300
        shadow-sm
        focus:border-sky-300 focus:ring focus:ring-sky-200 focus:ring-opacity-50`;
  const checkboxStyle = `rounded
        border-gray-300
        text-indigo-600
        shadow-sm
        focus:border-sky-300
        focus:ring
        focus:ring-offset-0
        focus:ring-sky-200
        focus:ring-opacity-50`;
  const dispatch = useAppDispatch();
  const credential = useAppSelector(selectCredential);
  const { username = "", password = "" } = credential;
  const config = useAppSelector(selectConfig);
  const { weighted, normalize, notify } = config;

  return (
    <RootLayout>
      <div className="grid grid-cols-1 gap-8">
        <label htmlFor="username" className="block">
          <span className="mb-1 text-slate-700 block font-medium">
            Username for eClass Login
          </span>
          <input
            type="text"
            placeholder=""
            className={textStyle}
            id="username"
            value={username}
            onChange={(e) =>
              dispatch(
                setCredential({ ...credential, username: e.target.value })
              )
            }
          />
        </label>
        <label htmlFor="password" className="block">
          <span className="mb-1 text-slate-700 block font-medium">
            Password for eClass Login
          </span>
          <input
            type="password"
            placeholder=""
            className={textStyle}
            id="password"
            value={password}
            onChange={(e) =>
              dispatch(
                setCredential({ ...credential, password: e.target.value })
              )
            }
          />
        </label>
        <label htmlFor="weighted" className="block">
          <input
            type="checkbox"
            className={checkboxStyle}
            id="weighted"
            checked={weighted}
            onChange={(e) =>
              dispatch(setConfig({ ...config, weighted: e.target.checked }))
            }
          />
          <span className="ml-2 text-slate-700 font-medium">
            Weighted grades (+10 for AP)
          </span>
        </label>
        <label htmlFor="normalize" className="block">
          <input
            type="checkbox"
            className={checkboxStyle}
            id="normalize"
            checked={normalize}
            onChange={(e) =>
              dispatch(setConfig({ ...config, normalize: e.target.checked }))
            }
          />
          <span className="ml-2 text-slate-700 font-medium">
            Normalize grades
          </span>
        </label>
        <label htmlFor="notify" className="block">
          <input
            type="checkbox"
            className={checkboxStyle}
            checked={notify}
            onChange={(e) =>
              dispatch(setConfig({ ...config, notify: e.target.checked }))
            }
          />
          <span className="ml-2 text-slate-700 font-medium">
            Notify me when grade drops
          </span>
        </label>
      </div>
    </RootLayout>
  );
}
