import { useEffect } from "react";
import showToast from "../../services/toast";

const Home = () => {
  useEffect(() => {
    const isRedirected = localStorage.getItem('Failed');
    if (isRedirected) {
      showToast({message:"Not authorized without signing in.",type:"error",position:"top-center"}),
      localStorage.removeItem('Failed');
    }
  }, []);
  return (
    <>
      <section className="Home">
        Home Page
      </section>
    </>
  )
}

export default Home
