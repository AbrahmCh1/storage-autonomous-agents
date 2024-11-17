using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class animationStateController : MonoBehaviour
{
    Animator animator;

    // Start is called before the first frame update
    void Start()
    {
        animator = GetComponent<Animator>();

    }

    // Update is called once per frame
    void Update()
    {
        bool isWalking = animator.GetBool("isWalking");
        bool isRotating = animator.GetBool("isRotating");
        bool isCarrying = animator.GetBool("isCarrying");
        float rotation = animator.GetFloat("rotation");


        if (Input.GetKey("w"))
        {
            animator.SetBool("isWalking", true);
        }
        if (!Input.GetKey("w"))
        {
            animator.SetBool("isWalking", false);
        }
        if (Input.GetKey("a"))
        {
            animator.SetBool("isRotating", true);
            animator.SetFloat("rotation", 1);
        }
        if (Input.GetKey("d"))
        {
            animator.SetBool("isRotating", true);
            animator.SetFloat("rotation", -1);
        }
        if (!Input.GetKey("a") && !Input.GetKey("d"))
        {
            animator.SetBool("isRotating", false);
        }
        if (Input.GetKey("e"))
        {
            animator.SetBool("isCarrying", true);
        }
        if (!Input.GetKey("e"))
        {
            animator.SetBool("isCarrying", false);
        }

        if (isWalking && !isRotating)
        {
            transform.Translate(0, 0, 0.03f);
        }

        if (rotation > 0 && isRotating)
        {
            transform.Rotate(0, -1, 0);
        }
        if (rotation < 0 && isRotating)
        {
            transform.Rotate(0, 1, 0);
        }

    }
}
