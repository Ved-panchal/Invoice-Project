import { useEffect } from "react";
import  showToast  from "../../services/toast"
import Pricing from "../Pricing/Pricing";

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
        <Pricing/>
      </section>
    </>
  )
}

export default Home
