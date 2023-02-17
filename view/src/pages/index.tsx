import RootLayout from "./layout";
import CourseCard from "@/components/CourseCard";
import Async from "react-async";
import { selectCredential, useAppSelector } from "@/store";

const loadCourses = (
  username: string | undefined,
  password: string | undefined
) => {
  if (!username || !password) return Promise.reject("No username or password");
  return fetch(
    `http://localhost:65535/courses?username=${username}&password=${password}`
  )
    .then((res) => (res.ok ? res : Promise.reject(res)))
    .then((res) => res.json())
    .then((data) =>
      data.map((course: any) => {
        let { course: name, teacher, grade, id, email } = course;
        return {
          name: name.split(": ")[1],
          teacher,
          score: parseInt(grade),
          id,
          email,
        };
      })
    );
};

export default function App() {
  const { username, password } = useAppSelector(selectCredential);
  return (
    <RootLayout>
      <div className="grid-flow gap-8 w-full place-items-center">
        <Async promiseFn={() => loadCourses(username, password)}>
          {({ data, error, isLoading }) => {
            if (isLoading)
              return Array(7)
                .fill(0)
                .map((_, i) => (
                  <div
                    className="animate-pulse w-64 h-64 bg-slate-50"
                    key={i}
                  ></div>
                ));
            if (error) {
              return <p>Something went wrong: {String(error)}</p>;
            }
            if (data)
              return data.map((course: any) => (
                <CourseCard key={course.id} {...course} />
              ));
          }}
        </Async>
      </div>
    </RootLayout>
  );
}
