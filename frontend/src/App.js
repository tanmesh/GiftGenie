import React from 'react';
// import GiftInput from './components/GiftInputs'
import Status from './components/Status';
import { QueryClient, QueryClientProvider } from 'react-query';

const queryClient = new QueryClient();

function Title({ name }) {
  return (
    <h1 className="text-3xl font-bold text-center">
      🎁{name}🎁
    </h1>
  )
}


function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8 bg-cover bg-center">
        <Title name="GiftGenie" />
        <Status />
      </div>
    </QueryClientProvider>
  );
}

export default App;