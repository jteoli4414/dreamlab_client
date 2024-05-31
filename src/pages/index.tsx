import Dashboard from "./dashboard";
import Login from "@/components/Login";
import { useSession } from "next-auth/react";
import scss from "./Home.module.scss";
import React from "react";

const Home: React.FC = () => {
  const { data: session } = useSession();

  return (
    <main className={scss.main}>
      {session && <Dashboard />}
      {!session && <Login />}
    </main>
  );
};

export default Home;
