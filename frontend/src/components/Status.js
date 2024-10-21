import React, { useState } from 'react';
import { Formik, Form, Field } from 'formik';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faXTwitter } from '@fortawesome/free-brands-svg-icons';

export default function GiftInput() {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [statusData, setStatusData] = useState({});
    const [error, setError] = useState(null);

    const validateForm = (values) => {
        const errors = {};
        if (values.price < 0) {
            errors.price = 'Price cannot be negative';
        }
        return errors;
    };

    const fetchData = async (values) => {
        try {
            console.log("Fetching data...");
            const response = await fetch('http://localhost:5000/generate_gift_suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST',
                },
                body: JSON.stringify({
                    "price_ceiling": values.price,
                    "twitter_handle": values.twitterHandle,
                    "additional_text": values.description,
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let buffer = '';
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (line.trim() !== '') {
                        try {
                            const parsedChunk = JSON.parse(line);
                            console.log("Received chunk:", parsedChunk);
                            setStatusData(prevData => ({
                                ...prevData,
                                ...parsedChunk
                            }));
                        } catch (e) {
                            console.error("Error parsing JSON:", e);
                        }
                    }
                }
            }

            if (buffer.trim() !== '') {
                try {
                    const parsedChunk = JSON.parse(buffer);
                    console.log("Received final chunk:", parsedChunk);
                    setStatusData(prevData => ({ ...prevData, ...parsedChunk }));
                } catch (e) {
                    console.error("Error parsing final JSON:", e);
                }
            }
        } catch (error) {
            console.error("Error fetching data:", error);
            setError(error.message);
        } finally {
            setIsSubmitting(false);
        }
    };

    const onSubmitForm = (values) => {
        setIsSubmitting(true);
        setStatusData({})
        fetchData(values);
    };

    const initialValues = {
        price: 30,
        twitterHandle: '',
        description: ''
    };


    const getStatusTitle = (key) => {
        const statusTitles = {
            "tweets": ( <>User Tweets <FontAwesomeIcon icon={faXTwitter} /></>),
            "interests": "User Interests",
            "categories": "Gift Categories",
            "gift_ideas": "Gift Ideas",
            "debating_ideas": "Debating Ideas",
            "reasoning": "Reasoning",
            "amazon_keywords": "Amazon Keywords",
            "amazon_recommendation": "Amazon Recommendation"
        };
        
        return statusTitles[key] || "Unknown Status";
    };

    const getNextKey = () => {
        const statusList = [
            "tweets",
            "interests",
            "categories",
            "gift_ideas",
            "debating_ideas",
            "reasoning",
            "amazon_keywords",
            "amazon_recommendation"
        ];

        const currentIndex = statusList.findIndex(key => Object.keys(statusData).includes(key));

        const tmp = statusList[currentIndex + 1];
        console.log('tmp: ', tmp)
        if (currentIndex !== -1) {
            return tmp;
        }
    };

    return (
        <>
            <Formik
                initialValues={initialValues}
                validate={validateForm}
                onSubmit={onSubmitForm}
            >
                {({ errors }) => (
                    <Form className="flex flex-col mt-4">
                        <div className="mb-4">
                            <label htmlFor="price" className="block text-sm font-medium text-gray-700">Enter Price:</label>
                            <Field
                                type="number"
                                name="price"
                                placeholder="Enter price"
                                className="px-3 py-2 border rounded-md"
                            />
                            {errors.price && <div className="text-red-500">*{errors.price}</div>}
                        </div>
                        <div className="mb-4">
                            <label htmlFor="twitterHandle" className="block text-sm font-medium text-gray-700">Enter Twitter Handle:</label>
                            <Field
                                type="text"
                                name="twitterHandle"
                                placeholder="Enter Twitter Handle"
                                className="px-3 py-2 border rounded-md"
                            />
                        </div>
                        <div className="mb-4">
                            <label htmlFor="description" className="block text-sm font-medium text-gray-700">Enter Description:</label>
                            <Field
                                type="text"
                                name="description"
                                placeholder="Enter description"
                                className="px-3 py-2 border rounded-md"
                            />
                        </div>
                        <button type="submit" className="mt-2 px-4 py-2 bg-blue-500 text-white rounded-md" disabled={isSubmitting}>
                            {isSubmitting ? 'Submitting...' : 'Start the genie!'}
                        </button>
                    </Form>
                )}
            </Formik>
            {error && <div className="text-red-500 mt-4">An error occurred: {error}. Please check the console for more details.</div>}
            {Object.keys(statusData).length > 0 && (
                <div className="mt-8">
                    <ol className="relative border-s border-gray-500 dark:border-gray-700 mt-10">
                        {Object.entries(statusData).map(([key, value]) => (
                            <li key={key} className="mb-10 ms-4">
                                <div className="absolute w-3 h-3 bg-gray-500 rounded-full mt-1.5 -start-1.5 border border-white dark:border-gray-900 dark:bg-gray-700"></div>
                                <time className="mb-1 text-lg font-normal leading-none text-black-500 dark:text-black-500">{getStatusTitle(key)}</time>
                                <ul >
                                    {key === 'amazon_recommendation' ? (
                                        Object.entries(value).map(([product, details], subIndex) => (
                                            <li key={subIndex} className="mb-4">
                                                <div className="max-w-sm rounded overflow-hidden shadow-lg bg-white dark:bg-gray-800 m-4">
                                                    <img src={details.image} alt={product} className="w-full h-48 object-cover" />
                                                    <div className="px-6 py-4">
                                                        <div className="font-bold text-xl mb-2">{product}</div>
                                                        <p className="text-gray-700 dark:text-gray-400 text-base">
                                                            {details.info}
                                                        </p>
                                                    </div>
                                                    <div className="px-6 pt-4 pb-2 flex items-center justify-between">
                                                        <span className="inline-block bg-gray-200 dark:bg-gray-700 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 dark:text-gray-200 mr-2 mb-2">{details.price}</span>
                                                        <span className="inline-block bg-gray-200 dark:bg-gray-700 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 dark:text-gray-200 mr-2 mb-2">Rating: {details.rating}</span>
                                                    </div>
                                                </div>
                                            </li>
                                        ))
                                    ) : (
                                        Array.isArray(value) ? value.map((item, subIndex) => (
                                            <li key={subIndex} className="mb-2 text-sm font-medium text-gray-600 dark:text-gray-500 mt-2">{item}</li>
                                        )) : (
                                            <li className="mb-2 text-sm font-medium text-gray-600 dark:text-gray-500 mt-2">{String(value)}</li>
                                        )
                                    )}
                                </ul>
                            </li>
                        ))}
                    </ol>
                </div>
            )}
        </>
    );
}