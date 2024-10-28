import React from 'react';
import { Formik, Form, Field } from 'formik';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faXTwitter } from '@fortawesome/free-brands-svg-icons';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import axios from 'axios';
import ReactMarkdown from 'react-markdown'

const API_BASE_URL = 'http://localhost:5000';

const initializeWorkflow = async (values) => {
    return axios.post(`${API_BASE_URL}/generate_gift_suggestions`, {
        price_ceiling: values.price,
        twitter_handle: values.twitterHandle,
        additional_text: values.description,
    });
};

const MarkdownContentWrapper = ({ value }) => {
    return (
        <div className="p-3 bg-gray-50 rounded-lg w-full overflow-x-auto">
            <div className="break-words whitespace-pre-wrap">
                {Array.isArray(value) ? (
                    value.map((item, index) => (
                        <div key={index} className="mb-2 prose prose-sm max-w-none">
                            <ReactMarkdown>{item}</ReactMarkdown>
                        </div>
                    ))
                ) : (
                    <div className="prose prose-sm max-w-none">
                        <ReactMarkdown>{value}</ReactMarkdown>
                    </div>
                )}
            </div>
        </div>
    );
};

const fetchGiftSuggestions = async () => {
    const response = await axios.get(`${API_BASE_URL}/generate_gift_suggestions`);

    let data = response.data;
    console.log(data)
    data.gift_reasoning = response.data.gift_reasoning.filter(item => item !== "");
    return data;
    // Dummy data for quick look
    // return {
    //     amazon_keywords: [],
    //     amazon_recommendation: [],
    //     debating_ideas: "# Debate Summary\n\n1. \"The New Jim Crow\" by Michelle Alexander\n   - **For**: The book is insightful and thought-provoking, great for those interested in politics, social issues, or law.\n   - **Against**: The book's complex themes may not be suitable for everyone, especially those not interested in politics or social issues.\n\n2. Bernie Sanders campaign button\n   - **For**: It's a piece of political memorabilia for fans of Bernie Sanders.\n   - **Against**: The gift is too specific and may not align with the recipient's political views.\n\n3. Black Lives Matter wristband\n   - **For**: It's a small, inexpensive gift that carries a powerful message and shows support for a vital social movement.\n   - **Against**: Wearing such a wristband may not be everyone's way of showing support.\n\n4. Mini Tarot Card Deck\n   - **For**: It's a fun, unique gift for someone interested in divination or spirituality.\n   - **Against**: Not everyone believes in or is comfortable with divination, making this gift potentially unsuitable.\n\n5. Rose Quartz Crystal Ball\n   - **For**: It's a beautiful, unique gift that can be used for healing and meditation or as a piece of decor.\n   - **Against**: Its use for healing and meditation is based on beliefs that not everyone shares.\n\n6. Instagram Logo Enamel Pin\n   - **For**: It's a fun, trendy gift for someone who loves Instagram or social media in general.\n   - **Against**: The gift assumes that the recipient uses and enjoys Instagram, which may not be the case.\n\n7. Miniature Gold Star Trophy\n   - **For**: It's a cute, thoughtful gift that can be given as a token of appreciation.\n   - **Against**: While it's a nice gesture, it may not be particularly useful or align with the recipient's interests.\n\n8. Custom Engraved Nameplate\n   - **For**: It's a personalized gift that can be customized with the recipient's name, showing thoughtfulness.\n   - **Against**: It may not be particularly useful and assumes that the recipient would want a nameplate.\n\n9. Organic Pumpkin Seed Butter\n   - **For**: It's a tasty, healthy gift perfect for someone who enjoys specialty food items.\n   - **Against**: The gift assumes that the recipient likes pumpkin seed butter, and being perishable, limits its longevity.\n\n10. Gourmet Trail Mix\n    - **For**: It's a delicious, healthy snack perfect for someone who enjoys gourmet food items.\n    - **Against**: The gift is perishable and assumes that the recipient enjoys trail mix.",
    //     gift_categories: "- Books on Politics/Social Issues\n- Political Memorabilia\n- Social Issue Awareness Merchandise\n- Tarot Cards/Crystal Balls\n- Social Media Themed Merchandise\n- Trophies/Awards\n- Personalized Recognition Gifts",
    //     gift_ideas: "Here are some affordable gift ideas under $30.0:\n\n1. [\"The New Jim Crow\" by Michelle Alexander](https://www.amazon.com/New-Jim-Crow-Incarceration-Colorblindness/dp/1595586431) - A thought-provoking book on politics and social issues.\n2. [Bernie Sanders campaign button](https://www.amazon.com/Bernie-Sanders-2020-Campaign-Button/dp/B07N7HJH8W) - A piece of political memorabilia for fans of Bernie Sanders.\n3. [Black Lives Matter wristband](https://www.amazon.com/Black-Lives-Matter-Wristband-Bracelet/dp/B08B3GQ2G7) - A social issue awareness merchandise to show support for the Black Lives Matter movement.\n4. [Mini Tarot Card Deck](https://www.amazon.com/Mini-Tarot-Card-Deck/dp/B08B3GQ2G7) - A compact and portable tarot card deck for those interested in divination.\n5. [Rose Quartz Crystal Ball](https://www.amazon.com/Jovivi-Natural-Quartz-Crystal-Sphere/dp/B01M7XWGZP) - A beautiful crystal ball made of rose quartz, often used for healing and meditation.\n6. [Instagram Logo Enamel Pin](https://www.amazon.com/Instagram-Social-Media-Enamel-Brooch/dp/B07QV1ZBZC) - A fun social media themed merchandise for Instagram lovers.\n7. [Miniature Gold Star Trophy](https://www.amazon.com/Gold-Star-Trophy-Award-Plate/dp/B07D7H8J6H) - A cute trophy/award that can be given as a token of appreciation.\n8. [Custom Engraved Nameplate](https://www.amazon.com/Custom-Engraved-Name-Plate-Adhesive/dp/B07B8B1SMB) - A personalized recognition gift that can be customized with the recipient's name.\n9. [Organic Pumpkin Seed Butter](https://www.amazon.com/Dastony-Organic-Pumpkin-Seed-Butter/dp/B00H2AAXMQ) - A tasty and healthy specialty food item made from high-quality organic pumpkin seeds.\n10. [Gourmet Trail Mix](https://www.amazon.com/Second-Nature-Simplicity-Medley-Ounce/dp/B00HZO4F2E) - A delicious mix of nuts and dried fruits, perfect for a quick and healthy snack.",
    //     gift_reasoning: [
    //         "Selected Gifts:",
    //         "",
    //         "1. \"The New Jim Crow\" by Michelle Alexander",
    //         "   - Rationale: This book can be a great gift for anyone interested in learning more about social issues and politics. It's thought-provoking and insightful, making it a valuable read for those who appreciate such themes.",
    //         "",
    //         "2. Custom Engraved Nameplate",
    //         "   - Rationale: This gift can be personalized, which shows thoughtfulness. Even if it may not be particularly useful, it's a nice keepsake that the recipient can display or use as they see fit.",
    //         "",
    //         "3. Gourmet Trail Mix",
    //         "   - Rationale: This is a versatile gift that can be enjoyed by most people. While it's perishable, it's a delicious and healthy snack that can be appreciated by those who enjoy gourmet food items.",
    //         "",
    //         "These three gifts were chosen because they cater to a wide range of interests - from social issues and politics to personal keepsakes and gourmet food items. While every gift has potential downsides, these three offer a balance of thoughtfulness, personalization, and general appeal."
    //     ],
    //     interests: "The analyzed tweets can be categorized into the following interest areas:\n\n- Politics\n- Social Issues\n- Prophecy/Fortune Telling\n- Social Media Interaction\n- Recognition/Awards",
    //     tweets: [
    //         "Fear of abortion bans?",
    //         "Will get 69.420%, as foretold in the prophecy https://t.co/ubFKrORwvA",
    //         "@cboyack 🔥🔥",
    //         "@TheRabbitHole84 Yup",
    //         "@GrantCardone @KamalaHQ 🤦‍♂️",
    //         "Super important https://t.co/5dmM5RLkcT",
    //         "@BigImpactHumans Yes",
    //         "@pmddomingos Yeah",
    //         "Congratulations Nancy of Arizona! https://t.co/F1wzkDQKf2",
    //         "@BasedBeffJezos Hell yeah!!"
    //     ]
    // };
};

const GiftInput = () => {
    const queryClient = useQueryClient();

    const { mutate, isLoading: isMutationLoading } = useMutation(initializeWorkflow, {
        onSuccess: () => {
            queryClient.invalidateQueries('giftSuggestions');
        },
    });

    const { data: giftSuggestions, isLoading: isQueryLoading, error } = useQuery(
        'giftSuggestions',
        fetchGiftSuggestions,
        {
            refetchInterval: 3000,
            enabled: isMutationLoading,
        }
    );

    const isLoading = isMutationLoading || isQueryLoading;

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
    };


    // Define orderedKeys at the top of the component
    const orderedKeys = [
        'tweets',
        'interests',
        'gift_categories',
        'gift_ideas',
        'debating_ideas',
        'gift_reasoning',
        'amazon_keywords',
        'amazon_recommendation'
    ];

    const getStatusTitle = (key) => {
        const statusTitles = {
            tweets: (<div className="flex items-center gap-2">User Tweets <FontAwesomeIcon icon={faXTwitter} /></div>),
            interests: "User Interests",
            gift_categories: "Gift Categories",
            debating_ideas: "Debating Ideas",
            gift_ideas: "Gift Ideas",
            gift_reasoning: "Reasoning",
            amazon_keywords: "Amazon Keywords",
            amazon_recommendation: "Amazon Recommendation",
        };
        return statusTitles[key] || "Unknown Status";
    };

    const renderAmazonRecommendation = (value) => (
        <div className="grid grid-cols-1 gap-6">
            {Object.entries(value).map(([product, details], subIndex) => (
                <div key={subIndex} className="transform transition-all duration-300 hover:scale-105">
                    <div className="bg-white rounded-xl overflow-hidden shadow-lg">
                        <div className="relative">
                            <img src={details.image} alt={product} className="w-full h-48 object-cover" />
                            <div className="absolute top-0 right-0 m-2 px-2 py-1 bg-blue-500 text-white text-sm rounded-lg">
                                {details.price === 'N/A' ? 'N/A' : `$${details.price}`}
                            </div>
                        </div>
                        <div className="p-6">
                            <h3 className="font-bold text-lg mb-2 text-gray-800">{details.title}</h3>
                            <div className="mt-4 flex items-center justify-between">
                                <div className="flex items-center">
                                    {[...Array(Math.floor(details.rating))].map((_, i) => (
                                        <svg key={i} className="w-4 h-4 text-yellow-400 fill-current" viewBox="0 0 20 20">
                                            <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                                        </svg>
                                    ))}
                                </div>
                                <span className="text-sm text-gray-600">Rating: {details.rating}</span>
                            </div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );

    const renderStatusItem = (key, value) => {
        if (!orderedKeys.includes(key)) return null; // Ignore keys not in the order

        return (
            <div key={key} className="mb-8 bg-white rounded-xl p-6 shadow-lg w-full max-w-md mx-auto overflow-visible">
                <h2 className="text-xl font-bold mb-4 text-gray-800 flex items-center gap-2">
                    {getStatusTitle(key)}
                </h2>
                <div className="space-y-3">
                    {key === 'amazon_recommendation'
                        ? renderAmazonRecommendation(value)
                        : <MarkdownContentWrapper value={value} />
                    }
                </div>
            </div>
        );
    };

    // Render the items in the specified order
    const renderAllStatusItems = (giftSuggestions) => {
        return orderedKeys.map((key) => {
            const value = giftSuggestions[key];
            return renderStatusItem(key, value);
        });
    };

    return (
        <div >
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-12 mt-5">
                    <p className="text-lg text-gray-600">Let our AI help you find the perfect gift!</p>
                </div>

                <div className="max-w-xl mx-auto bg-white rounded-xl shadow-lg p-6 mb-8">
                    <Formik
                        initialValues={initialValues}
                        validate={validateForm}
                        onSubmit={(values) => mutate(values)}
                    >
                        {({ errors }) => (
                            <Form className="space-y-6">
                                <div>
                                    <label htmlFor="price" className="block text-sm font-medium text-gray-700 mb-2">
                                        Budget
                                    </label>
                                    <Field
                                        type="number"
                                        name="price"
                                        placeholder="Enter your budget"
                                        className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    />
                                    {errors.price && <p className="mt-2 text-sm text-red-600">*{errors.price}</p>}
                                </div>

                                <div>
                                    <label htmlFor="twitterHandle" className="block text-sm font-medium text-gray-700 mb-2">
                                        Twitter Handle
                                    </label>
                                    <div className="relative">
                                        <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-500">@</span>
                                        <Field
                                            type="text"
                                            name="twitterHandle"
                                            placeholder="username"
                                            className="w-full pl-8 px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                                        Additional Details
                                    </label>
                                    <Field
                                        as="textarea"
                                        name="description"
                                        placeholder="Any additional information about the recipient..."
                                        className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        rows="4"
                                    />
                                </div>

                                <button
                                    type="submit"
                                    disabled={isLoading}
                                    className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                                >
                                    {isLoading ? (
                                        <div className="flex items-center gap-2">
                                            ✨ The Genie is working its magic...
                                            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                            </svg>
                                        </div>
                                    ) : 'Start the Genie! ✨'}
                                </button>
                            </Form>
                        )}
                    </Formik>
                </div>

                {error && (
                    <div className="max-w-xl mx-auto p-4 mb-8 bg-red-50 rounded-lg">
                        <p className="text-red-600">{error.message}</p>
                    </div>
                )}
                {giftSuggestions && (
                    <div className="mt-12 space-y-8">
                        {renderAllStatusItems(giftSuggestions)}
                    </div>
                )}
            </div>
        </div>
    );
};

export default GiftInput;
