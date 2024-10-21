import { useState } from 'react';
import { Formik, Form, Field } from 'formik';


export default function GiftInput() {
    const [isSubmit, setSubmitting] = useState(false);

    const onSubmitForm = (values) => {
        setSubmitting(true);
        console.log(values);
        
    };

    const validateForm = (values) => {
        const errors = {};
        if (values.price < 0) {
            errors.price = 'Price cannot be negative';
        }
        return errors;
    };

    const initialValues = {
        price: 30,
        twitterHandle: '',
        description: ''
    }

    return (
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
                    <button type="submit" className="mt-2 px-4 py-2 bg-blue-500 text-white rounded-md" disabled={isSubmit}>
                        {
                            isSubmit ?
                                'Submitting...' :
                                'Start the genie!'
                        }
                    </button>
                </Form>
            )}
        </Formik>
    )
};