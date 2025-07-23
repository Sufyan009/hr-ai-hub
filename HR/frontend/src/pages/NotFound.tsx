import { useLocation } from "react-router-dom";
import { useEffect } from "react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100" role="main" aria-label="404 Not Found Page">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4" role="heading" aria-level="1">404</h1>
        <p className="text-xl text-gray-600 mb-4" role="alert">Oops! Page not found</p>
        <a href="/" className="text-blue-500 hover:text-blue-700 underline" aria-label="Return to Home">
          Return to Home
        </a>
      </div>
    </div>
  );
};

export default NotFound;

// Add a NotAuthorized page for forbidden access
export const NotAuthorized = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100" role="main" aria-label="403 Forbidden Page">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4" role="heading" aria-level="1">403</h1>
        <p className="text-xl text-gray-600 mb-4" role="alert">You are not authorized to access this page.</p>
        <a href="/" className="text-blue-500 hover:text-blue-700 underline" aria-label="Return to Home">
          Return to Home
        </a>
      </div>
    </div>
  );
};
