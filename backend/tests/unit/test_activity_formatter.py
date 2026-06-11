"""Unit tests for deterministic activity answer formatting."""

from ai.activity_formatter import (
    ActivityIntent,
    detect_activity_intent,
    try_format_activity_answer,
)
from ai.context_cleaner import clean_context_text
from ai.retriever import _extract_activity_passage


SAMPLE_PASSAGE = """
Activity 6.1: Let us try and find out
- Take two transparent glass or plastic pipes of the same length (about 25 cm), but of different diameters, as shown in Fig. 6.5.
- Take two good-quality rubber balloons. Attach them to one end of each pipe.
- Clamp the pipes on a stand as shown in Fig. 6.5.
- Now, fill both the pipes with water up to the same level about halfway.
- Observe what happens to the balloons.
- Do both balloons bulge? Do they bulge to the same extent?
What can you infer from this activity? You must have observed that the two balloons bulge to the same extent. Why is it so? Notice that because of the different diameters, the weight of water in the two pipes is different. However, the bulge in both the balloons is the same. This means that the weight of water in the pipes could not be responsible for the extent of the bulge of the balloons. Could it be that the water column is exerting pressure? Yes, it is the pressure exerted by the water column which is responsible for the bulge.
Pour some more water in any one of the pipes used in Fig. 6.5. Observe the bulge of the balloon. Do you see any relation between the amount of bulge of the rubber balloon and the height of the water column in the pipe? You must have observed that the bulge of the balloon increases as the height of the water column increases.
Thus, as the height of the water column in the pipe increases, the pressure at the bottom of the pipe also increases, which causes the balloon to bulge more. So, we can say that the pressure exerted by a liquid in a vessel depends on the height of its column.
"""


def test_format_activity_includes_key_science_points():
    """Formatted activity should state height dependence, not diameter dependence."""
    answer = try_format_activity_answer(SAMPLE_PASSAGE, "Activity 6.1")
    assert answer is not None
    assert "different diameters" in answer
    assert "same length" in answer
    assert "bulge to the same extent" in answer
    assert "height of the water column" in answer or "height of its column" in answer
    assert "Pour some more water" in answer


def test_format_activity_procedure_is_numbered():
    """Procedure steps should be listed without LLM-style paraphrase."""
    answer = try_format_activity_answer(SAMPLE_PASSAGE, "Activity 6.1")
    assert answer is not None
    assert "1. Take two transparent glass or plastic pipes" in answer
    assert "Procedure" in answer


SAMPLE_PASSAGE_6_2 = """
Activity 6.2: Let us find out
- Take a used plastic bottle and remove its cap. Make four small holes near the bottom around the sides using a needle or a nail. Make sure that the holes are at the same height from the bottom as shown in Fig. 6.7.
- Seal the holes with a tape and fill the bottle with water.
- Now, remove the tape from all holes at the same time.
- What do you observe?
You observe water flowing out through the holes on the sides of the bottle. What can you infer from this observation? It indicates that water also exerts pressure on the sides of a container. Therefore, we can conclude that liquids exert pressure not only at the bottom of the container, but also on its sides. In fact liquids exert pressure in all directions.
You must have seen water spurting out like a fountain from leaking joints or holes in water pipes. Can you explain why this happens? Is it due to the pressure exerted by water on the walls of the pipes?
"""


MOON_ACTIVITY_PASSAGE = """
activity to understand how the illuminated portion of the Moon, as seen by us, changes when its position changes with respect to the Sun.
Activity 11.2: Let us explore
- Take a small soft ball and insert a stick into it (Fig. 11.4a). This represents the Moon.
- Go to a dark open place (at night), and ask a teacher or guardian to shine a torchlight towards you from about 3 m to represent light coming from the Sun or stand near an electric lamp. Your head represents the Earth.
- Now hold the ball at arm's length in one hand such that it is slightly above your head as shown in Fig. 11.4b. Keep the ball at position E towards the direction of the lamp. Does the portion of the ball facing you appear to be illuminated or not?
- Turn around slowly, in the anti-clockwise direction, with your arm outstretched as shown in Fig. 11.4b and keep looking at the ball. Does the shape of the illuminated portion change? Is the line separating the illuminated and non-illuminated portions of the ball curved?
- Was your observation similar to the changing shape of the illuminated portion of ball shown in Fig. 11.4c? The shape of the illuminated portion of the ball, as seen by you, changes depending on where the ball is with respect to the lamp.
When the ball is held opposite to the direction of the lamp (at A), you are facing the entire illuminated portion of the ball, just like the full Moon day. On the other hand, when the ball is held towards the direction of the lamp (at E), you are facing the non-illuminated portion of the ball, and cannot see the illuminated portion of the ball at all. This is similar to the new Moon day. Notice how in other cases, the line separating the illuminated and non-illuminated portions of the ball appears curved (Fig. 11.4c), similar to the shape of the illuminated portion of the Moon viewed from the Earth on other days.
"""


def test_format_activity_11_2_is_concise():
    """Moon-phase activity should stay brief and avoid dumping figure captions."""
    answer = try_format_activity_answer(MOON_ACTIVITY_PASSAGE, "Activity 11.2")
    assert answer is not None
    assert len(answer) < 1100
    assert "full Moon" in answer
    assert "new Moon" in answer
    assert answer.count("Take a small soft ball") == 1
    assert "A A B B" not in answer
    assert "beryllium" not in answer.lower()


def test_format_activity_6_2_liquid_side_pressure():
    """Activity 6.2 should explain side pressure without Activity 6.1 balloon content."""
    answer = try_format_activity_answer(SAMPLE_PASSAGE_6_2, "Activity 6.2")
    assert answer is not None
    assert "plastic bottle" in answer
    assert "water flowing out through the holes" in answer
    assert "liquids exert pressure" in answer
    assert "all directions" in answer
    assert "Balloon bulges" not in answer
    assert "Fig. 6.6" not in answer
    assert answer.count("remove the tape") == 1


ACTIVITY_5_7_PASSAGE = """
Activity 5.7: Let us experiment
- Take two balloons, a length of thread, and a woollen cloth.
- Inflate two balloons and hang them in such a way that they do not touch each other.
- Rub both balloons with the woollen cloth and release them. Be careful not to touch the rubbed balloons with your fingers.
What do you observe? We observe that the balloons move away from each other as if they are repelling each other.
What do we infer from these observations? Fig. 5.9: Charged balloons
We found that the two similarly charged balloons repel each other whereas a charged balloon and the woollen cloth attract each other. As the similarly charged balloons repelled each other, we can infer that similar (like) charges repel each other. Both the rubbing object and the rubbed object get charged but they acquire opposite kind of charges. Their attraction shows that opposite kind (unlike) of charges attract each other. The force exerted by a charged body on another charged body is called electrostatic force. It is a non-contact force.
"""


def test_detect_activity_conclusion_intent():
    intent = detect_activity_intent("what is the conclusion we can draw from activity 5.7")
    assert intent == ActivityIntent.CONCLUSION


def test_format_activity_5_7_conclusion_only():
    answer = try_format_activity_answer(
        ACTIVITY_5_7_PASSAGE,
        "Activity 5.7",
        intent=ActivityIntent.CONCLUSION,
    )
    assert answer is not None
    assert "repel" in answer.lower()
    assert "attract" in answer.lower()
    assert "Procedure" not in answer
    assert "Take two balloons" not in answer


def test_detect_activity_explain_intent():
    intent = detect_activity_intent("Explain activity 5.7")
    assert intent == ActivityIntent.FULL
