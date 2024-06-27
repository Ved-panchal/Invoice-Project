import { useEffect } from "react";
import Toast, { showToast } from "../../services/toasts"

const Home = () => {
  useEffect(() => {
    const isRedirected = localStorage.getItem('Failed');
    if (isRedirected) {
      showToast("Not authorized without signing in.","error"),
      localStorage.removeItem('Failed');
    }
  }, []);
  return (
    <>
      <section className="Home">
        Home Page
        <Toast/>
      </section>
    </>
  )
}

export default Home
