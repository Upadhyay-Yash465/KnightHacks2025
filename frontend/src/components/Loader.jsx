import React from 'react';

const Loader = ({ message = "Loading..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12">
      <div className="relative">
        <div className="w-20 h-20 border-4 border-gray-600 border-t-orange-500 rounded-full animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-blue-500 rounded-full animate-pulse"></div>
        </div>
      </div>
      <p className="mt-6 text-xl text-gray-300 font-medium">{message}</p>
    </div>
  );
};

export default Loader;
